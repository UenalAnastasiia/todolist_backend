from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TodoItemSerializer
from .models import TodoItem

# Create your views here.
class LoginView(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class TodoItemView(APIView):
    # Nur angemeldete User können die todos sehen
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        todos = TodoItem.objects.filter(author=request.user)
        serializer = TodoItemSerializer(todos, many=True)
        return Response(serializer.data)
    
    
    def post(self, request, format=None):
        serializer = TodoItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    
    def delete(self, request, pk, format=None):
        todo = self.get_queryset(pk)
        todo.delete()
        return Response(status.HTTP_204_NO_CONTENT)


    def get_queryset(self, pk):
        try:
            return TodoItem.objects.get(author=self.request.user, id=pk)
        except TodoItem.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    
    
    def patch(self, request, pk):
        todoItem_object = self.get_queryset(pk)
        serializer = TodoItemSerializer(todoItem_object, data=request.data, partial=True) # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status.HTTP_400_BAD_REQUEST)
            