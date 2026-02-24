from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from .serializers import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password

# --------------------    LoginViewSet    --------------------


class LoginViewSet(generics.GenericAPIView):
    """
    User Login ViewSet
    """

    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            response_data = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "tokens": user.tokens,
            }
            return Response(
                {
                    "status": True,
                    "message": "Login successfully",
                    "data": response_data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong",  # Fixed typo
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

class NoteViewSet(generics.GenericAPIView):
    serializer_class = NoteSerializer

    def post(self, request):
        
        serializer = NoteSerializer(data = request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Note Store successfully",
                    "data": {}
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": False,
                "message": "Something went wrong",
                "data": {},
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request,pk):

        get_note = Note.objects.filter(id=pk).first()
        if not get_note:
            return Response(
                {
                    "status": False,
                    "message": "Note not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        
        serializer = NoteSerializer(get_note, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Note updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

        return Response(
                {
                    "status": False,
                    "message": "Something went wrong",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
    
    def get(self, request):
        queryset = Note.objects.all()
        serializer = NoteSerializer(queryset, many=True)
        return Response(
            {
                "status": True,
                "message": "Note list",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class UserCreateAPIView(generics.GenericAPIView):
    serializer_class = UserCreateSerializer
    queryset = UserModel.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "status": True,
                "message": "User created successfully",
                "data": {
                    # "id": user.id,
                    # "username": user.username,
                    # "email": user.email,
                    # "tokens": user.tokens
                }
            }, status=status.HTTP_200_OK)
        error_messages = []
        for field, errors in serializer.errors.items():
            error_messages.extend(errors)
        return Response({"status": False,"message": error_messages[0]}, status=status.HTTP_200_OK)

    def get(self, request):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response({"status": False,"message": "User List Fatch successfully.","data":serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, id):
        user = get_object_or_404(UserModel, id=id)
        user.delete()
        return Response({"status": True,"message": "User deleted successfully."}, status=status.HTTP_200_OK)



class ChangePasswordAPIView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request, id):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = UserModel.objects.get(id=id)
            except UserModel.DoesNotExist:
                return Response({"status": False,"message": "User not found."}, status=status.HTTP_200_OK)

            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()

            return Response({"status": True,"message": "Password changed successfully."}, status=status.HTTP_200_OK)

        # Custom error format
        error_messages = []
        for field, errors in serializer.errors.items():
            print("serializer.errors.items()")
            error_messages.extend(errors)
        
        return Response({"status": False,"message": error_messages[0]}, status=status.HTTP_200_OK)


# python manage.py runserver 192.168.1.83:8001