from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Create your views here.


@api_view(["POST"])
def identify(request):
    return Response({}, status=status.HTTP_201_CREATED)
