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

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if EmailAddress.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError(
                    "A user is already registered with this e-mail address."
                )
        return email

    def validate_password(self, password):
        # Remove password validation temporarily
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
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        try:
            # Attempt to authenticate
            user = authenticate(
                username=attrs.get('username'),
                password=attrs.get('password')
            )

            if not user:
                raise serializers.ValidationError({
                    'error': 'Invalid username or password'
                })

            if not user.is_active:
                raise serializers.ValidationError({
                    'error': 'This account has been disabled'
                })

            # Add user to validated data
            attrs['user'] = user
            return attrs

        except Exception as e:
            raise serializers.ValidationError({
                'error': str(e)
            })
