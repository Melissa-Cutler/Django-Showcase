from django.urls import path

from . import views

app_name = 'capitalcallapp'
urlpatterns = [
    path('new-commitment/', views.newCommitment, name='new-commitment'),
    path('new-investment/', views.newInvestment, name='new-investment'),
    path('', views.index, name='index'),
]
