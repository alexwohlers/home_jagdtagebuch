from django.db import models
from django.contrib.auth.models import User
from datetime import date

class JagdLog(models.Model):
    WILDART_CHOICES = [
        ('Schalenwild', [
            ('rehbock', 'Rehbock'),
            ('ricke', 'Ricke'),
            ('rehkitz', 'Rehkitz'),
            ('schwarzwild', 'Schwarzwild'),
            ('rotwild', 'Rotwild'),
            ('damwild', 'Damwild'),
            ('muffelwild', 'Muffelwild'),
            ('gamswild', 'Gamswild'),
        ]),
        ('Niederwild', [
            ('hase', 'Hase'),
            ('wildkaninchen', 'Wildkaninchen'),
            ('fasan', 'Fasan'),
            ('rebhuhn', 'Rebhuhn'),
            ('wildente', 'Wildente'),
            ('wildgans', 'Wildgans'),
            ('wildtaube', 'Wildtaube'),
        ]),
        ('Raubwild', [
            ('fuchs', 'Fuchs'),
            ('dachs', 'Dachs'),
            ('marder', 'Marder'),
            ('waschbaer', 'Waschbaer'),
            ('marderhund', 'Marderhund'),
        ]),
        ('Sonstiges', [
            ('sonstiges', 'Sonstiges'),
        ]),
    ]
    
    GESCHLECHT_CHOICES = [
        ('m', 'Maennlich'),
        ('w', 'Weiblich'),
        ('u', 'Unbekannt'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wildart = models.CharField(max_length=50, choices=WILDART_CHOICES)
    datum = models.DateField(default=date.today)
    uhrzeit = models.TimeField(null=True, blank=True)
    revier = models.CharField(max_length=200, blank=True)
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHT_CHOICES, default='u')
    gewicht = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    alter_geschaetzt = models.CharField(max_length=50, blank=True)
    jagdart = models.CharField(max_length=100, blank=True)
    waffe = models.CharField(max_length=200, blank=True)
    entfernung = models.IntegerField(null=True, blank=True)
    notizen = models.TextField(blank=True)
    wetter = models.CharField(max_length=100, blank=True)
    temperatur = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datum', '-uhrzeit']
        verbose_name = 'Jagdeintrag'
        verbose_name_plural = 'Jagdeintraege'

    def __str__(self):
        return f'{self.get_wildart_display()} - {self.datum}'

    def get_wildart_emoji(self):
        emoji_map = {
            'rehbock': '', 'ricke': '', 'rehkitz': '',
            'schwarzwild': '', 'rotwild': '', 'damwild': '',
            'muffelwild': '', 'gamswild': '',
            'hase': '', 'wildkaninchen': '', 'fasan': '',
            'rebhuhn': '', 'wildente': '', 'wildgans': '', 'wildtaube': '',
            'fuchs': '', 'dachs': '', 'marder': '',
            'waschbaer': '', 'marderhund': '',
            'sonstiges': '',
        }
        return emoji_map.get(self.wildart, '')
