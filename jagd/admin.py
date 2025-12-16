from django.contrib import admin
from .models import JagdLog, Revier, Hochsitz

@admin.register(JagdLog)
class JagdLogAdmin(admin.ModelAdmin):
    list_display = ['wildart', 'datum', 'revier_ref', 'hochsitz_ref', 'geschlecht', 'gewicht', 'user']
    list_filter = ['wildart', 'datum', 'revier_ref', 'geschlecht']
    search_fields = ['wildart', 'notizen']
    date_hierarchy = 'datum'

@admin.register(Revier)
class RevierAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
    list_filter = ['user']
    search_fields = ['name', 'beschreibung']

@admin.register(Hochsitz)
class HochsitzAdmin(admin.ModelAdmin):
    list_display = ['name', 'typ', 'revier', 'aktiv', 'user']
    list_filter = ['typ', 'revier', 'aktiv', 'user']
    search_fields = ['name', 'beschreibung']
