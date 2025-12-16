#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jagdtagebuch.settings')
django.setup()

from jagd.models import Waffe, JagdLog

print("=== Waffen ===")
for w in Waffe.objects.all():
    print(f"  ID {w.pk}: {w.name} - {w.kaliber}")

print("\n=== JagdLog Einträge mit Waffe ===")
for e in JagdLog.objects.all():
    if e.waffe:
        print(f"  ID {e.pk}: waffe='{e.waffe}'")
