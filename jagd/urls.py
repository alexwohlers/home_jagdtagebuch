from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('neu/', views.eintrag_neu, name='eintrag_neu'),
    path('liste/', views.liste, name='liste'),
    path('<int:pk>/', views.eintrag_detail, name='eintrag_detail'),
    path('<int:pk>/bearbeiten/', views.eintrag_bearbeiten, name='eintrag_bearbeiten'),
    path('<int:pk>/loeschen/', views.eintrag_loeschen, name='eintrag_loeschen'),
    path('register/', views.register, name='register'),
]
