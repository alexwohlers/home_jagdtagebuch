import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jagdtagebuch.settings')
django.setup()
from jagd.models import JagdLog, Waffe

# Die Einträge 2 und 3 hatten ursprünglich 7x64, also 98er
waffe_98er = Waffe.objects.get(pk=1)
JagdLog.objects.filter(pk__in=[2,3]).update(waffe_ref=waffe_98er)
print('Einträge 2 und 3 auf 98er aktualisiert')

for e in JagdLog.objects.all().order_by('pk'):
    print(f'ID {e.pk}: {e.waffe_ref}')
