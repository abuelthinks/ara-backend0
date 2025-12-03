from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from core.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ParentRegisterSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_parent(request):
    """
    Register a new parent account
    Expects: {
        "email": "parent@example.com",
        "first_name": "John",
        "phone": "+63 9XX XXX XXXX",
        "password": "SecurePass123",
        "confirm_password": "SecurePass123"
    }
    Returns: {
        "access": "jwt_token",
        "refresh": "refresh_token",
        "user": {user_data}
    }
    """
    serializer = ParentRegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': {
                'user_id': str(user.user_id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'role': user.role,
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Custom login endpoint that returns JWT token pair and user data.
    Expects: {"username": "...", "password": "..."}
    Returns: {"access": "...", "refresh": "...", "user": {...}}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    return Response({
        'access': access_token,
        'refresh': refresh_token,
        'user': {
            'user_id': str(user.user_id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint - blacklist refresh token to invalidate it.
    Expects: {"refresh": "..."}
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()  # Requires TOKEN_BLACKLIST in settings
        
        return Response(
            {'message': 'Successfully logged out'}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    """Get current authenticated user info"""
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
