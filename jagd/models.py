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
    # Revier und Hochsitz als ForeignKey (Revier required, Hochsitz optional)
    revier_ref = models.ForeignKey('Revier', on_delete=models.PROTECT, null=True, blank=True, related_name='jagd_eintraege', verbose_name='Revier')
    hochsitz_ref = models.ForeignKey('Hochsitz', on_delete=models.SET_NULL, null=True, blank=True, related_name='jagd_eintraege', verbose_name='Hochsitz')
    # Waffe als ForeignKey (optional)
    waffe_ref = models.ForeignKey('Waffe', on_delete=models.SET_NULL, null=True, blank=True, related_name='jagd_eintraege', verbose_name='Waffe')
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHT_CHOICES, default='u', verbose_name='Geschlecht')
    gewicht = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='Gewicht (kg)')
    alter_geschaetzt = models.CharField(max_length=100, blank=True, verbose_name='Geschätztes Alter')
    jagdart = models.CharField(max_length=100, blank=True, verbose_name='Jagdart')
    entfernung = models.PositiveIntegerField(null=True, blank=True, verbose_name='Schussentfernung (m)')
    notizen = models.TextField(blank=True, verbose_name='Notizen')
    wetter = models.CharField(max_length=100, blank=True, verbose_name='Wetterbedingungen')
    temperatur = models.IntegerField(null=True, blank=True, verbose_name='Temperatur (°C)')
    trophaee = models.BooleanField(default=False, verbose_name='Trophäe aufgehoben')
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


class Revier(models.Model):
    """Reviere für die Hochsitz-Verwaltung"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviere')
    name = models.CharField(max_length=200, verbose_name='Reviername')
    beschreibung = models.TextField(blank=True, verbose_name='Beschreibung')
    groesse_ha = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Größe (ha)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Revier'
        verbose_name_plural = 'Reviere'
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return self.name


class Hochsitz(models.Model):
    """Hochsitze innerhalb eines Reviers"""
    
    TYP_CHOICES = [
        ('kanzel', '🏠 Kanzel'),
        ('leiter', '🪜 Leitersitz'),
        ('druckjagdbock', '🎯 Drückjagdbock'),
        ('ansitzschirm', '🏕️ Ansitzschirm'),
        ('sonstiges', '📍 Sonstiges'),
    ]
    
    ZUSTAND_CHOICES = [
        ('gut', '✅ Gut'),
        ('reparatur', '🔧 Reparatur nötig'),
        ('schlecht', '⚠️ Schlecht'),
        ('neu', '🆕 Neu'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hochsitze')
    revier = models.ForeignKey(Revier, on_delete=models.CASCADE, related_name='hochsitze', verbose_name='Revier')
    name = models.CharField(max_length=200, verbose_name='Name/Bezeichnung')
    typ = models.CharField(max_length=50, choices=TYP_CHOICES, default='kanzel', verbose_name='Typ')
    beschreibung = models.TextField(blank=True, verbose_name='Beschreibung')
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='GPS Breitengrad')
    gps_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='GPS Längengrad')
    zustand = models.CharField(max_length=20, choices=ZUSTAND_CHOICES, default='gut', verbose_name='Zustand')
    baujahr = models.PositiveIntegerField(null=True, blank=True, verbose_name='Baujahr')
    letzte_kontrolle = models.DateField(null=True, blank=True, verbose_name='Letzte Kontrolle')
    notizen = models.TextField(blank=True, verbose_name='Notizen')
    aktiv = models.BooleanField(default=True, verbose_name='Aktiv')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hochsitz'
        verbose_name_plural = 'Hochsitze'
        ordering = ['revier__name', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.revier.name})"
    
    def get_typ_emoji(self):
        for value, label in self.TYP_CHOICES:
            if value == self.typ:
                return label.split()[0]
        return '📍'


class Waffe(models.Model):
    """Waffenverwaltung"""
    
    TYP_CHOICES = [
        ('buechse', '🎯 Büchse'),
        ('flinte', '🔫 Flinte'),
        ('drilling', '🔫 Drilling'),
        ('kombiniert', '🔫 Kombinierte Waffe'),
        ('kurzwaffe', '🔫 Kurzwaffe'),
        ('sonstiges', '📍 Sonstiges'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waffen')
    name = models.CharField(max_length=200, verbose_name='Bezeichnung')
    typ = models.CharField(max_length=50, choices=TYP_CHOICES, default='buechse', verbose_name='Waffentyp')
    hersteller = models.CharField(max_length=100, blank=True, verbose_name='Hersteller')
    modell = models.CharField(max_length=100, blank=True, verbose_name='Modell')
    kaliber = models.CharField(max_length=100, verbose_name='Kaliber')
    seriennummer = models.CharField(max_length=100, blank=True, verbose_name='Seriennummer')
    kaufdatum = models.DateField(null=True, blank=True, verbose_name='Kaufdatum')
    wbk_nummer = models.CharField(max_length=50, blank=True, verbose_name='WBK-Nummer')
    notizen = models.TextField(blank=True, verbose_name='Notizen')
    aktiv = models.BooleanField(default=True, verbose_name='Aktiv')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Waffe'
        verbose_name_plural = 'Waffen'
        ordering = ['name']
    
    def __str__(self):
        if self.kaliber:
            return f"{self.name} ({self.kaliber})"
        return self.name
    
    def get_typ_emoji(self):
        for value, label in self.TYP_CHOICES:
            if value == self.typ:
                return label.split()[0]
        return '🔫'

