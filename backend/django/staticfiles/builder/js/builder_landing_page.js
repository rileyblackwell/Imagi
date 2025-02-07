$(document).ready(function() {
    // CSRF token setup
    var csrftoken = Cookies.get('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Handle project deletion confirmation
    $('.delete-project-form').on('submit', function(e) {
        if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
});
