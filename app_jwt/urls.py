from django.conf.urls import url
from .views import  authenticate_user, create_user_api, get_user_details, update_user_details

urlpatterns = [
	url(r'^create/$', create_user_api),
	url(r'^detail/$', get_user_details),
	url(r'^update/$', update_user_details),
	url(r'^obtain_token/$', authenticate_user),
]