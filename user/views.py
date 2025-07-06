from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateSuperUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()

    @extend_schema(
        summary="Create a new superuser",
        description="Allows creation of a new superuser account. No authentication required.",
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer

    @extend_schema(
        summary="User login and obtain auth token",
        description="Authenticate user with email and password and return a token.",
        responses={200: AuthTokenSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="Retrieve or update authenticated user",
        description="Get or update the currently authenticated user profile. Authentication required.",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update authenticated user",
        description="Update fields of the authenticated user. Password changes are supported.",
        responses={200: UserSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update authenticated user",
        description="Partially update fields of the authenticated user.",
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)