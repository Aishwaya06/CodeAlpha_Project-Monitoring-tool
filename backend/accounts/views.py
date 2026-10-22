import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

def user_data(user):
    return {"id": user.id, "username": user.username, "email": user.email, "first_name": user.first_name, "last_name": user.last_name}

@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf(request):
    return Response({"detail": "CSRF cookie set."})

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = str(request.data.get("username", "")).strip()
    email = str(request.data.get("email", "")).strip().lower()
    password = str(request.data.get("password", ""))
    if not username or not email or not password:
        return Response({"detail": "Username, email, and password are required."}, status=400)
    if User.objects.filter(username__iexact=username).exists():
        return Response({"username": ["A user with that username already exists."]}, status=400)
    try:
        validate_password(password)
    except ValidationError as exc:
        return Response({"password": list(exc.messages)}, status=400)
    user = User.objects.create_user(username=username, email=email, password=password,
                                    first_name=str(request.data.get("first_name", "")).strip(),
                                    last_name=str(request.data.get("last_name", "")).strip())
    login(request, user)
    return Response(user_data(user), status=201)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    user = authenticate(request, username=str(request.data.get("username", "")), password=str(request.data.get("password", "")))
    if not user:
        return Response({"detail": "Invalid username or password."}, status=400)
    login(request, user)
    return Response(user_data(user))

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response(status=204)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(user_data(request.user))
