from django.contrib import admin
from .models import JagdLog

@admin.register(JagdLog)
class JagdLogAdmin(admin.ModelAdmin):
    list_display = ['wildart', 'datum', 'revier', 'geschlecht', 'gewicht', 'user']
    list_filter = ['wildart', 'datum', 'revier', 'geschlecht']
    search_fields = ['wildart', 'revier', 'notizen']
    date_hierarchy = 'datum'
