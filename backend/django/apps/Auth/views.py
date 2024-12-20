from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User  # Add this import
from django.conf import settings  # Add this import
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.password_validation import validate_password, ValidationError
from django.contrib.auth import update_session_auth_hash

User = get_user_model()

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('landing_page')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Imagi, {user.username}!")
            return redirect('landing_page')
    else:
        form = UserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing_page')

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "auth/password_reset_email.html"
                    context = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'Imagi',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, context)
                    try:
                        send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)  # Use settings.DEFAULT_FROM_EMAIL
                    except Exception as e:
                        messages.error(request, f"There was an error sending email: {e}")
                        return render(request, "auth/password_reset.html", {'form': form})
                    
                    return redirect("password_reset_done")
            
            # Even if user doesn't exist, redirect to done page for security
            return redirect("password_reset_done")
    
    form = PasswordResetForm()
    return render(request, "auth/password_reset.html", {"form": form})

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    API endpoint for confirming password reset and setting new password
    """
    try:
        uid = urlsafe_base64_decode(request.data.get('uid')).decode()
        token = request.data.get('token')
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')
        
        if not all([uid, token, new_password1, new_password2]):
            return Response(
                {'errors': {'detail': 'Missing required fields'}},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if new_password1 != new_password2:
            return Response(
                {'errors': {'new_password2': 'Passwords do not match'}},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user = User.objects.get(pk=uid)
        
        if not default_token_generator.check_token(user, token):
            return Response(
                {'errors': {'detail': 'Invalid or expired reset token'}},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.set_password(new_password1)
        user.save()
        
        return Response({'detail': 'Password has been reset successfully'})
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'errors': {'detail': 'Invalid reset link'}},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    API endpoint for requesting a password reset
    """
    email = request.data.get('email')
    if not email:
        return Response(
            {'errors': {'email': 'Email is required'}},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Always return success to prevent email enumeration
    try:
        user = User.objects.get(email=email)
        subject = "Password Reset Requested"
        email_template_name = "auth/password_reset_email.html"
        context = {
            "email": user.email,
            'domain': request.META['HTTP_HOST'],
            'site_name': 'Imagi',
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http',
        }
        email_content = render_to_string(email_template_name, context)
        
        try:
            send_mail(
                subject,
                email_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
        except Exception as e:
            # Log the error but don't expose it to the user
            print(f"Error sending password reset email: {e}")
    except User.DoesNotExist:
        # User not found, but we don't want to reveal this
        pass

    return Response({
        'detail': 'If an account exists with this email, you will receive password reset instructions.'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    API endpoint for changing user password
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not all([old_password, new_password]):
        return Response(
            {'errors': {'detail': 'Both old and new passwords are required'}},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify old password
    if not user.check_password(old_password):
        return Response(
            {'errors': {'old_password': 'Current password is incorrect'}},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate new password
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response(
            {'errors': {'new_password': e.messages}},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Set new password
    user.set_password(new_password)
    user.save()

    # Update session auth hash to prevent logout
    update_session_auth_hash(request, user)

    return Response({'detail': 'Password successfully updated'})
