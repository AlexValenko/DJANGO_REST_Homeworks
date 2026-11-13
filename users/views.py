from rest_framework.generics import DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView

from .models import User
from .serializer import UserSerializer

# class UserCreateApiView(CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


class UserListApiView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveApiView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdateApiView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDestroyApiView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
