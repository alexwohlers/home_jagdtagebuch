#!/usr/bin/env python
"""
Skript zur Verknüpfung der bestehenden Einträge mit den Waffen
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jagdtagebuch.settings')
django.setup()

from jagd.models import JagdLog, Waffe

# Mapping von alten Text-Werten zu Waffen-IDs
# 7x64 -> 98er (ID 1)
# .308 Win -> SM12 (ID 2)

print("=== Waffen in Datenbank ===")
for w in Waffe.objects.all():
    print(f"  ID {w.pk}: {w.name} - {w.kaliber}")

print("\n=== Verknüpfe Einträge ===")

# Hole die Waffen
waffe_98er = Waffe.objects.filter(kaliber='7x64').first()
waffe_sm12 = Waffe.objects.filter(kaliber='.308 Win').first()

print(f"Waffe für 7x64: {waffe_98er}")
print(f"Waffe für .308 Win: {waffe_sm12}")

# Verknüpfe alle Einträge die noch keine waffe_ref haben
eintraege_ohne_waffe = JagdLog.objects.filter(waffe_ref__isnull=True)
print(f"\nEinträge ohne Waffe-Referenz: {eintraege_ohne_waffe.count()}")

# Da die alte waffe-Spalte weg ist, verknüpfen wir basierend auf anderen Kriterien
# oder setzen eine Standard-Waffe

# Für jetzt setzen wir die SM12 als Standard, da das die häufigste war
if waffe_sm12:
    updated = eintraege_ohne_waffe.update(waffe_ref=waffe_sm12)
    print(f"Einträge aktualisiert mit SM12: {updated}")

print("\n=== Fertig ===")
for e in JagdLog.objects.all().order_by('-datum')[:5]:
    print(f"  ID {e.pk}: {e.datum} - Waffe: {e.waffe_ref}")
