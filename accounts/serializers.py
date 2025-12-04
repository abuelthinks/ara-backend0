from rest_framework import serializers
from core.models import User


class ParentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'password', 'confirm_password', 'phone']

    def validate_password(self, value):
        """Validate password strength"""
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        return value

    def validate(self, data):
        """Validate that passwords match and email is unique"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        # Check for existing email in User model
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already registered."})
        
        return data

    def create(self, validated_data):
        """Create new user with PARENT role"""
        validated_data.pop('confirm_password')
        phone = validated_data.pop('phone', '')
        
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            password=validated_data['password'],
            role='PARENT',
            phone=phone if phone else ''
        )
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serialize user data for API responses"""
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone']
        read_only_fields = ['user_id', 'username']
