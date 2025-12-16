from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('neu/', views.eintrag_neu, name='eintrag_neu'),
    path('liste/', views.liste, name='liste'),
    path('liste/detailliert/', views.liste_detailliert, name='liste_detailliert'),
    path('<int:pk>/', views.eintrag_detail, name='eintrag_detail'),
    path('<int:pk>/bearbeiten/', views.eintrag_bearbeiten, name='eintrag_bearbeiten'),
    path('<int:pk>/loeschen/', views.eintrag_loeschen, name='eintrag_loeschen'),
    path('register/', views.register, name='register'),
    # Benutzerverwaltung (nur für Superuser)
    path('benutzer/', views.benutzer_liste, name='benutzer_liste'),
    path('benutzer/neu/', views.benutzer_neu, name='benutzer_neu'),
    path('benutzer/<int:pk>/bearbeiten/', views.benutzer_bearbeiten, name='benutzer_bearbeiten'),
    path('benutzer/<int:pk>/loeschen/', views.benutzer_loeschen, name='benutzer_loeschen'),
    # Revier-Verwaltung
    path('reviere/', views.revier_liste, name='revier_liste'),
    path('reviere/neu/', views.revier_neu, name='revier_neu'),
    path('reviere/<int:pk>/bearbeiten/', views.revier_bearbeiten, name='revier_bearbeiten'),
    path('reviere/<int:pk>/loeschen/', views.revier_loeschen, name='revier_loeschen'),
    # Hochsitz-Verwaltung
    path('hochsitze/', views.hochsitz_liste, name='hochsitz_liste'),
    path('hochsitze/revier/<int:revier_pk>/', views.hochsitz_liste, name='hochsitz_liste_revier'),
    path('hochsitze/neu/', views.hochsitz_neu, name='hochsitz_neu'),
    path('hochsitze/neu/revier/<int:revier_pk>/', views.hochsitz_neu, name='hochsitz_neu_revier'),
    path('hochsitze/<int:pk>/', views.hochsitz_detail, name='hochsitz_detail'),
    path('hochsitze/<int:pk>/bearbeiten/', views.hochsitz_bearbeiten, name='hochsitz_bearbeiten'),
    path('hochsitze/<int:pk>/loeschen/', views.hochsitz_loeschen, name='hochsitz_loeschen'),
    # Waffen-Verwaltung
    path('waffen/', views.waffe_liste, name='waffe_liste'),
    path('waffen/neu/', views.waffe_neu, name='waffe_neu'),
    path('waffen/<int:pk>/bearbeiten/', views.waffe_bearbeiten, name='waffe_bearbeiten'),
    path('waffen/<int:pk>/loeschen/', views.waffe_loeschen, name='waffe_loeschen'),
]
