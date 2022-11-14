from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login_view),
    path('',signup_view),
    path('home/',home_view),
    path('logout/',logout_view),
    path('wallet/',wallet_view),
    path('send/',send_view),
    path('receive/',receive_view),
    path('requests/',requests_view)
]