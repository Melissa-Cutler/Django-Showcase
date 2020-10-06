from django.urls import path

from . import views

app_name = 'capitalcallapp'
urlpatterns = [
    path('new-investment/', views.newInvestment, name='new-investment'),
    path('', views.index, name='index'),
]
