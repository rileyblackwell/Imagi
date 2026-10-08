"""
The app half of the Operate dashboard: uptime checks and page-view counting.

Uptime: Imagi requests the app's live address and records whether it answered
(any final status below 400 after following redirects) and how long the
response took to start. The address is user-supplied and fetched from Imagi's
servers, so every hop is resolved and refused unless it points at a public
internet address — never localhost, the private network, or cloud metadata.

Page views: the app's tag posts each page load to a public beacon endpoint
keyed by AppMonitor.site_key. A view only counts when it comes from the live
address's host, so the build preview and copies of the tag elsewhere don't
inflate the numbers.
"""

import datetime
import hashlib
import ipaddress
import socket
import time
from statistics import median
from urllib.parse import urljoin, urlsplit

import requests
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from ..models import AppMonitor, PageView, UptimeCheck

CHECK_TIMEOUT_SECONDS = 8
MAX_REDIRECTS = 3
# A dashboard visit re-checks the app only when the last check is older than
# this, so opening Operate twice in a row doesn't hit the app twice.
CHECK_FRESH_FOR = datetime.timedelta(minutes=5)
WINDOW_DAYS = 30
TRAFFIC_SERIES_DAYS = 14
USER_AGENT = 'ImagiUptime/1.0 (+https://imagi.up.railway.app)'


class UnsafeURL(ValueError):
    """The address isn't a public http(s) URL Imagi is willing to request."""


def normalize_live_url(raw: str) -> str:
    """Trim, default the scheme to https, and drop any fragment."""
    value = (raw or '').strip()
    if not value:
        return ''
    if '://' not in value:
        value = f'https://{value}'
    parts = urlsplit(value)
    path = parts.path or '/'
    query = f'?{parts.query}' if parts.query else ''
    return f'{parts.scheme.lower()}://{parts.netloc.lower()}{path}{query}'


def assert_public_url(url: str) -> None:
    """Raise UnsafeURL unless `url` is http(s) and resolves only to public IPs."""
    parts = urlsplit(url)
    if parts.scheme not in ('http', 'https'):
        raise UnsafeURL('Use an http:// or https:// address.')
    if parts.username or parts.password:
        raise UnsafeURL("Leave the username and password out of the address.")
    host = parts.hostname
    if not host:
        raise UnsafeURL('That address has no host name.')
    try:
        port = parts.port or (443 if parts.scheme == 'https' else 80)
    except ValueError:
        raise UnsafeURL('That address has an invalid port.')
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        raise UnsafeURL(f"Couldn't find {host} on the internet.")
    for info in infos:
        address = ipaddress.ip_address(info[4][0].split('%', 1)[0])
        if not address.is_global:
            raise UnsafeURL(f'{host} points at a private address Imagi can’t check.')


def _request(url: str) -> requests.Response:
    """GET `url`, following up to MAX_REDIRECTS redirects, each one vetted."""
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        assert_public_url(current)
        response = requests.get(
            current,
            timeout=CHECK_TIMEOUT_SECONDS,
            allow_redirects=False,
            stream=True,  # headers are enough; never download the page body
            headers={'User-Agent': USER_AGENT},
        )
        response.close()
        location = response.headers.get('Location')
        if response.is_redirect and location:
            current = urljoin(current, location)
            continue
        return response
    raise requests.TooManyRedirects(f'More than {MAX_REDIRECTS} redirects.')


def run_check(monitor: AppMonitor) -> UptimeCheck:
    """Request the live address once and record the result."""
    url = monitor.live_url
    started = time.monotonic()
    status_code = None
    error = ''
    try:
        response = _request(url)
        status_code = response.status_code
        is_up = status_code < 400
        if not is_up:
            error = f'Answered with HTTP {status_code}.'
    except UnsafeURL as exc:
        is_up, error = False, str(exc)
    except requests.Timeout:
        is_up, error = False, f'No answer within {CHECK_TIMEOUT_SECONDS} seconds.'
    except requests.RequestException:
        is_up, error = False, "Couldn't connect."
    elapsed_ms = int((time.monotonic() - started) * 1000)
    return UptimeCheck.objects.create(
        project=monitor.project,
        url=url,
        is_up=is_up,
        status_code=status_code,
        response_ms=elapsed_ms if status_code is not None else None,
        error=error[:255],
    )


def check_is_stale(monitor: AppMonitor) -> bool:
    if not monitor.live_url:
        return False
    latest = monitor.project.operate_uptime_checks.filter(url=monitor.live_url).first()
    return latest is None or timezone.now() - latest.checked_at > CHECK_FRESH_FOR


# -- Page views -------------------------------------------------------------------


def visitor_hash(site_key: str, ip: str, user_agent: str) -> str:
    """A daily-rotating id for one visitor, built so it can't be reversed."""
    day = timezone.localdate().isoformat()
    raw = f'{site_key}|{day}|{ip}|{user_agent}'.encode()
    return hashlib.sha256(raw).hexdigest()[:32]


def host_of(url: str) -> str:
    try:
        return (urlsplit(url).hostname or '').lower()
    except ValueError:
        return ''


def same_site(source_host: str, live_host: str) -> bool:
    """`www.` on either side doesn't make it a different site."""
    def bare(host):
        return host[4:] if host.startswith('www.') else host
    return bool(source_host) and bare(source_host) == bare(live_host)


# -- Dashboard payload ------------------------------------------------------------


def app_summary(project) -> dict:
    """Everything the dashboard's app half shows."""
    monitor = AppMonitor.objects.filter(project=project).first()
    live_url = monitor.live_url if monitor else ''
    since = timezone.now() - datetime.timedelta(days=WINDOW_DAYS)

    checks = project.operate_uptime_checks.filter(checked_at__gte=since)
    if live_url:
        checks = checks.filter(url=live_url)
    latest = checks.first()
    check_count = checks.count()
    up_count = checks.filter(is_up=True).count()
    response_times = list(
        checks.filter(is_up=True, response_ms__isnull=False)
        .values_list('response_ms', flat=True)[:500]
    )

    views = project.operate_page_views.filter(created_at__gte=since)
    view_count = views.count()
    visitor_count = views.values('visitor').distinct().count()

    today = timezone.localdate()
    series_start = today - datetime.timedelta(days=TRAFFIC_SERIES_DAYS - 1)
    daily = {
        row['day']: row['visitors']
        for row in (
            project.operate_page_views
            .filter(created_at__date__gte=series_start)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(visitors=Count('visitor', distinct=True))
        )
    }
    traffic = []
    for offset in range(TRAFFIC_SERIES_DAYS):
        day = series_start + datetime.timedelta(days=offset)
        traffic.append({
            'date': day.isoformat(),
            'label': f'{day:%b} {day.day}',
            'visitors': daily.get(day, 0),
        })

    return {
        'live_url': live_url,
        'site_key': monitor.site_key if monitor else '',
        'check_stale': bool(monitor and check_is_stale(monitor)),
        'status': None if latest is None else {
            'is_up': latest.is_up,
            'checked_at': latest.checked_at,
            'status_code': latest.status_code,
            'response_ms': latest.response_ms,
            'error': latest.error,
        },
        'uptime': {
            'percent': round(up_count / check_count * 100, 2) if check_count else None,
            'checks': check_count,
        },
        'response_ms': {
            'latest': latest.response_ms if latest and latest.is_up else None,
            'median': int(median(response_times)) if response_times else None,
        },
        'traffic': {
            'visitors': visitor_count,
            'page_views': view_count,
            'daily': traffic,
        },
    }
