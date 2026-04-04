from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('service/<str:service_slug>/', views.service_detail, name='service-detail'),
    path('contact/', views.contact, name='contact'),
    path('rate/', views.rate, name='rate'),
]