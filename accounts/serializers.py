from rest_framework import serializers
from core.models import User


class ParentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'confirm_password', 'phone']

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
        """Validate fields and derive username if omitted"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        # Ensure email is unique
        email = data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already registered."})
        
        # Require both first_name and last_name
        first = (data.get('first_name') or '').strip()
        last = (data.get('last_name') or '').strip()
        if not first:
            raise serializers.ValidationError({"first_name": "First name is required."})
        if not last:
            raise serializers.ValidationError({"last_name": "Last name is required."})
        
        # Derive username if blank: first + last (no spaces, lowercased)
        username = (data.get('username') or '').strip()
        if not username:
            username = (first + last).replace(' ', '').lower()
        
        if not username:
            # Fallback to email local part
            username = email.split('@')[0]
        
        # Enforce unique username
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already taken."})
        
        data['email'] = email
        data['username'] = username
        data['first_name'] = first
        data['last_name'] = last
        return data

    def create(self, validated_data):
        """Create new user with PARENT role"""
        validated_data.pop('confirm_password')
        phone = validated_data.pop('phone', '')
        username = validated_data.pop('username')
        first = validated_data.pop('first_name', '')
        last = validated_data.pop('last_name', '')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first,
            last_name=last,
            password=password,
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
