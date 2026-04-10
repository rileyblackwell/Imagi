from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

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
        email = email.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
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

    def save(self, request):
        user = User.objects.create_user(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            password=self.validated_data['password'],
        )
        return user

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
