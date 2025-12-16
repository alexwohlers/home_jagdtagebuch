#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jagdtagebuch.settings')
django.setup()

from jagd.models import JagdLog
from django.template import Template, Context

e = JagdLog.objects.get(pk=11)
print(f"Gewicht aus DB: {e.gewicht} (Typ: {type(e.gewicht)})")

# Test simple template
t = Template("Gewicht: {{ eintrag.gewicht }}")
c = Context({"eintrag": e})
print(f"Template Output: '{t.render(c)}'")

# Test mit default filter
t2 = Template("Gewicht: {{ eintrag.gewicht|default:'' }}")
print(f"Template mit default: '{t2.render(c)}'")

# Alle Felder testen
print("\n--- Alle Felder ---")
print(f"wildart: {e.wildart}")
print(f"datum: {e.datum}")
print(f"gewicht: {e.gewicht}")
print(f"jagdart: {e.jagdart}")
print(f"entfernung: {e.entfernung}")
print(f"temperatur: {e.temperatur}")
print(f"notizen: {e.notizen}")
