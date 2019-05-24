from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

import jwt

from django.contrib.auth.signals import user_logged_in

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.serializers import jwt_payload_handler

from django_jwt import settings
from .serializers import UserSerializer
from .models import User


@api_view(['POST'])
@permission_classes([AllowAny, ])
def create_user_api(request):
	user = request.data
	serializer = UserSerializer(data=user)
	serializer.is_valid(raise_exception=True)
	serializer.save()
	return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_user_details(request, *args, **kwargs):
	serializer = UserSerializer(request.user)
	return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, ])
def update_user_details(request, *args, **kwargs):
	serializer_data = request.data
	serializer = UserSerializer(
		request.user, data=serializer_data, partial=True
	)
	serializer.is_valid(raise_exception=True)
	serializer.save()
	return Response(serializer.data, status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
	try:
		email = request.data['email']
		password = request.data['password']

		user = User.objects.get(email=email, password=password)
		if user:
			try:
				payload = jwt_payload_handler(user)
				token = jwt.encode(payload, settings.SECRET_KEY)
				user_details = {}
				user_details['name'] = "%s %s" % (user.first_name, user.last_name)
				user_details['token'] = token
				user_logged_in.send(sender=user.__class__,
									request=request, user=user)
				return Response(user_details, status=status.HTTP_200_OK)

			except Exception as e:
				raise e
		else:
			res = {
				'error': 'can not authenticate with the given credentials or the account has been deactivated'}
			return Response(res, status=status.HTTP_403_FORBIDDEN)
	except KeyError:
		res = {'error': 'please provide a email and a password'}
		return Response(res)