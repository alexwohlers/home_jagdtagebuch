from django.db import models
from django.contrib.auth.models import User


class JagdLog(models.Model):
    """Jagdtagebuch - Dokumentation erlegter Wildtiere"""
    
    WILDART_CHOICES = [
        # Schalenwild
        ('Schalenwild', (
            ('rehbock', '🦌 Rehbock'),
            ('rehgeis', '🦌 Rehgeiß'),
            ('rehkitz', '🦌 Rehkitz'),
            ('hirsch', '🦌 Rothirsch'),
            ('hirschkuh', '🦌 Hirschkuh'),
            ('hirschkalb', '🦌 Hirschkalb'),
            ('damhirsch', '🦌 Damhirsch'),
            ('damtier', '🦌 Damtier'),
            ('damkalb', '🦌 Damkalb'),
            ('keiler', '🐗 Keiler'),
            ('bache', '🐗 Bache'),
            ('ueberlaeufer', '🐗 Überläufer'),
            ('frischling', '🐗 Frischling'),
            ('mufflon', '🐏 Mufflon'),
        )),
        # Niederwild
        ('Niederwild', (
            ('feldhase', '🐰 Feldhase'),
            ('wildkaninchen', '🐰 Wildkaninchen'),
            ('fasan_hahn', '🐓 Fasanhahn'),
            ('fasan_henne', '🐓 Fasanhenne'),
            ('rebhuhn', '🐦 Rebhuhn'),
            ('wachtel', '🐦 Wachtel'),
            ('taube', '🕊️ Wildtaube'),
            ('stockente', '🦆 Stockente'),
            ('gaense', '🪿 Wildgans'),
        )),
        # Raubwild
        ('Raubwild', (
            ('fuchs', '🦊 Fuchs'),
            ('dachs', '🦡 Dachs'),
            ('marder', '🐾 Marder'),
            ('waschbaer', '🦝 Waschbär'),
            ('marderhund', '🐕 Marderhund'),
            ('nutria', '🦫 Nutria'),
        )),
        # Sonstiges
        ('Sonstiges', (
            ('kraehe', '🐦‍⬛ Krähe'),
            ('elster', '🐦 Elster'),
            ('sonstiges', '🎯 Sonstiges'),
        )),
    ]
    
    GESCHLECHT_CHOICES = [
        ('m', '♂ Männlich'),
        ('w', '♀ Weiblich'),
        ('u', '? Unbekannt'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jagd_logs')
    wildart = models.CharField(max_length=50, verbose_name='Wildart')
    wildart_custom = models.CharField(max_length=100, blank=True, verbose_name='Eigene Wildart')
    datum = models.DateField(verbose_name='Erlegungsdatum')
    uhrzeit = models.TimeField(null=True, blank=True, verbose_name='Uhrzeit')
    revier = models.CharField(max_length=200, blank=True, verbose_name='Revier/Ort')
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHT_CHOICES, default='u', verbose_name='Geschlecht')
    gewicht = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='Gewicht (kg)')
    alter_geschaetzt = models.CharField(max_length=100, blank=True, verbose_name='Geschätztes Alter')
    jagdart = models.CharField(max_length=100, blank=True, verbose_name='Jagdart')
    waffe = models.CharField(max_length=100, blank=True, verbose_name='Waffe/Kaliber')
    entfernung = models.PositiveIntegerField(null=True, blank=True, verbose_name='Schussentfernung (m)')
    notizen = models.TextField(blank=True, verbose_name='Notizen')
    wetter = models.CharField(max_length=100, blank=True, verbose_name='Wetterbedingungen')
    temperatur = models.IntegerField(null=True, blank=True, verbose_name='Temperatur (°C)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Jagdtagebuch-Eintrag'
        verbose_name_plural = 'Jagdtagebuch-Einträge'
        ordering = ['-datum', '-uhrzeit', '-created_at']
    
    def __str__(self):
        return f"{self.get_wildart_display()} am {self.datum}"
    
    def get_wildart_display(self):
        """Gibt die lesbare Wildart zurück"""
        if self.wildart == 'sonstiges' and self.wildart_custom:
            return f"🎯 {self.wildart_custom}"
        for group, choices in self.WILDART_CHOICES:
            for value, label in choices:
                if value == self.wildart:
                    return label
        return self.wildart
    
    def get_wildart_emoji(self):
        """Gibt nur das Emoji der Wildart zurück"""
        display = self.get_wildart_display()
        if display and len(display) > 0:
            return display.split()[0]
        return '🎯'

