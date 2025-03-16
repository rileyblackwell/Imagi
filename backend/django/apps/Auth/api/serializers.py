from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.account import app_settings as allauth_settings
from allauth.account.models import EmailAddress

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source='profile.balance', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'balance')
        read_only_fields = ('id', 'balance')

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    def validate_username(self, username):
        username = username.strip()
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError(
                "This username is already taken. Please choose another one."
            )
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if EmailAddress.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError(
                    "A user is already registered with this e-mail address."
                )
        return email

    def validate_password(self, password):
        # Basic password validation
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return password

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"password_confirmation": "Passwords don't match"})
        return data

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        try:
            adapter.save_user(request, user, self)
            setup_user_email(request, user, [])
            return user
        except Exception as e:
            # Log the detailed error but return a user-friendly message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"User registration error: {str(e)}")
            raise serializers.ValidationError("Unable to complete registration. Please try again.")

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username', '').strip()
        password = attrs.get('password', '')
        
        # Validation for empty fields
        if not username:
            raise serializers.ValidationError({
                'username': 'Username is required'
            })
        
        if not password:
            raise serializers.ValidationError({
                'password': 'Password is required'
            })
        
        try:
            # Check if user exists first
            user_exists = User.objects.filter(username__iexact=username).exists()
            if not user_exists:
                raise serializers.ValidationError({
                    'error': 'No account found with this username'
                })
            
            # Attempt to authenticate
            user = authenticate(
                username=username,
                password=password
            )

            if not user:
                raise serializers.ValidationError({
                    'error': 'Invalid password. Please try again'
                })

            if not user.is_active:
                raise serializers.ValidationError({
                    'error': 'This account has been disabled'
                })

            # Add user to validated data
            attrs['user'] = user
            return attrs

        except serializers.ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Log the error but provide a user-friendly message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Login validation error: {str(e)}")
            raise serializers.ValidationError({
                'error': 'Login failed. Please try again later'
            })
