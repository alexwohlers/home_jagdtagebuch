from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from datetime import date, timedelta
from .models import JagdLog, Revier, Hochsitz

def superuser_required(user):
    return user.is_superuser

def get_saison_dates():
    today = date.today()
    if today.month >= 4:
        saison_start = date(today.year, 4, 1)
        saison_ende = date(today.year + 1, 3, 31)
    else:
        saison_start = date(today.year - 1, 4, 1)
        saison_ende = date(today.year, 3, 31)
    return saison_start, saison_ende

@login_required
def dashboard(request):
    saison_start, saison_ende = get_saison_dates()
    eintraege = JagdLog.objects.filter(user=request.user)
    saison_eintraege = eintraege.filter(datum__gte=saison_start, datum__lte=saison_ende)
    
    # Korrekte Wildart-Schlüssel basierend auf WILDART_CHOICES
    rehwild_arten = ['rehbock', 'rehgeis', 'rehkitz', 'hirsch', 'hirschkuh', 'hirschkalb', 
                     'damhirsch', 'damtier', 'damkalb', 'mufflon']
    schwarzwild_arten = ['keiler', 'bache', 'ueberlaeufer', 'frischling']
    niederwild_arten = ['feldhase', 'wildkaninchen', 'fasan_hahn', 'fasan_henne', 
                        'rebhuhn', 'wachtel', 'taube', 'stockente', 'gaense']
    raubwild_arten = ['fuchs', 'dachs', 'marder', 'waschbaer', 'marderhund', 'nutria']
    
    # Statistik für aktuelle Saison
    saison_stats = {
        'gesamt': saison_eintraege.count(),
        'rehwild': saison_eintraege.filter(wildart__in=rehwild_arten).count(),
        'schwarzwild': saison_eintraege.filter(wildart__in=schwarzwild_arten).count(),
        'niederwild': saison_eintraege.filter(wildart__in=niederwild_arten).count(),
        'raubwild': saison_eintraege.filter(wildart__in=raubwild_arten).count(),
    }
    
    # Statistik für alle Jahre (Gesamt)
    gesamt_stats = {
        'gesamt': eintraege.count(),
        'rehwild': eintraege.filter(wildart__in=rehwild_arten).count(),
        'schwarzwild': eintraege.filter(wildart__in=schwarzwild_arten).count(),
        'niederwild': eintraege.filter(wildart__in=niederwild_arten).count(),
        'raubwild': eintraege.filter(wildart__in=raubwild_arten).count(),
    }
    
    saison_eintraege_liste = saison_eintraege.order_by('-datum')
    wildarten_stats = saison_eintraege.values('wildart').annotate(count=Count('wildart')).order_by('-count')
    reviere = eintraege.filter(revier_ref__isnull=False).values('revier_ref__name').annotate(count=Count('revier_ref')).order_by('-count')[:10]
    
    # Trophäen-Liste sortiert nach Wildart-Größe (Schalenwild > Schwarzwild > Raubwild > Niederwild)
    wildart_reihenfolge = (
        rehwild_arten + schwarzwild_arten + raubwild_arten + niederwild_arten + 
        ['kraehe', 'elster', 'sonstiges']
    )
    trophaeen = list(eintraege.filter(trophaee=True))
    trophaeen.sort(key=lambda x: wildart_reihenfolge.index(x.wildart) if x.wildart in wildart_reihenfolge else 999)
    
    # Wildart-Labels für Template
    wildart_labels = {}
    for group, choices in JagdLog.WILDART_CHOICES:
        for value, label in choices:
            wildart_labels[value] = label
    
    context = {
        'saison_start': saison_start,
        'saison_ende': saison_ende,
        'saison_stats': saison_stats,
        'gesamt_stats': gesamt_stats,
        'saison_eintraege': saison_eintraege_liste,
        'wildarten_stats': wildarten_stats,
        'wildart_labels': wildart_labels,
        'reviere': reviere,
        'trophaeen': trophaeen,
    }
    return render(request, 'jagd/dashboard.html', context)

def fix_year(datum_str):
    """Korrigiert 2-stellige Jahre auf 4-stellig (z.B. 0025-04-23 -> 2025-04-23)"""
    if datum_str and len(datum_str) >= 10:
        year = datum_str[:4]
        if year.startswith('00'):
            datum_str = '20' + datum_str[2:]
    return datum_str

@login_required
def eintrag_neu(request):
    reviere = Revier.objects.filter(user=request.user)
    hochsitze = Hochsitz.objects.filter(user=request.user, aktiv=True).select_related('revier')
    waffen = Waffe.objects.filter(user=request.user, aktiv=True)
    
    if request.method == 'POST':
        eintrag = JagdLog(user=request.user)
        eintrag.wildart = request.POST.get('wildart', 'rehbock')
        eintrag.wildart_custom = request.POST.get('wildart_custom', '')
        eintrag.datum = fix_year(request.POST.get('datum', str(date.today())))
        uhrzeit = request.POST.get('uhrzeit')
        if uhrzeit:
            eintrag.uhrzeit = uhrzeit
        # Revier und Hochsitz als Referenz
        revier_id = request.POST.get('revier_ref')
        if revier_id:
            eintrag.revier_ref = Revier.objects.filter(pk=revier_id, user=request.user).first()
        hochsitz_id = request.POST.get('hochsitz_ref')
        if hochsitz_id:
            eintrag.hochsitz_ref = Hochsitz.objects.filter(pk=hochsitz_id, user=request.user).first()
        # Waffe als Referenz
        waffe_id = request.POST.get('waffe_ref')
        if waffe_id:
            eintrag.waffe_ref = Waffe.objects.filter(pk=waffe_id, user=request.user).first()
        eintrag.geschlecht = request.POST.get('geschlecht', 'u')
        gewicht = request.POST.get('gewicht')
        if gewicht:
            eintrag.gewicht = gewicht
        eintrag.alter_geschaetzt = request.POST.get('alter_geschaetzt', '')
        eintrag.jagdart = request.POST.get('jagdart', '')
        entfernung = request.POST.get('entfernung')
        if entfernung:
            eintrag.entfernung = entfernung
        eintrag.notizen = request.POST.get('notizen', '')
        eintrag.wetter = request.POST.get('wetter', '')
        temperatur = request.POST.get('temperatur')
        if temperatur:
            eintrag.temperatur = temperatur
        eintrag.trophaee = request.POST.get('trophaee') == 'on'
        eintrag.save()
        messages.success(request, 'Waidmannsheil! Eintrag wurde gespeichert.')
        return redirect('dashboard')
    
    heute = date.today().strftime('%Y-%m-%d')
    letzter_eintrag = JagdLog.objects.filter(user=request.user).first()
    context = {
        'WILDART_CHOICES': JagdLog.WILDART_CHOICES,
        'GESCHLECHT_CHOICES': JagdLog.GESCHLECHT_CHOICES,
        'heute': heute,
        'letzter_eintrag': letzter_eintrag,
        'reviere': reviere,
        'hochsitze': hochsitze,
        'waffen': waffen,
    }
    return render(request, 'jagd/eintrag_form.html', context)

@login_required
def eintrag_detail(request, pk):
    eintrag = get_object_or_404(JagdLog, pk=pk, user=request.user)
    return render(request, 'jagd/eintrag_detail.html', {'eintrag': eintrag})

@login_required
def eintrag_bearbeiten(request, pk):
    eintrag = get_object_or_404(JagdLog, pk=pk, user=request.user)
    reviere = Revier.objects.filter(user=request.user)
    hochsitze = Hochsitz.objects.filter(user=request.user, aktiv=True).select_related('revier')
    waffen = Waffe.objects.filter(user=request.user, aktiv=True)
    
    if request.method == 'POST':
        eintrag.wildart = request.POST.get('wildart', eintrag.wildart)
        eintrag.wildart_custom = request.POST.get('wildart_custom', '')
        eintrag.datum = fix_year(request.POST.get('datum', str(eintrag.datum)))
        uhrzeit = request.POST.get('uhrzeit')
        eintrag.uhrzeit = uhrzeit if uhrzeit else None
        # Revier und Hochsitz als Referenz
        revier_id = request.POST.get('revier_ref')
        eintrag.revier_ref = Revier.objects.filter(pk=revier_id, user=request.user).first() if revier_id else None
        hochsitz_id = request.POST.get('hochsitz_ref')
        eintrag.hochsitz_ref = Hochsitz.objects.filter(pk=hochsitz_id, user=request.user).first() if hochsitz_id else None
        # Waffe als Referenz
        waffe_id = request.POST.get('waffe_ref')
        eintrag.waffe_ref = Waffe.objects.filter(pk=waffe_id, user=request.user).first() if waffe_id else None
        eintrag.geschlecht = request.POST.get('geschlecht', eintrag.geschlecht or 'u')
        gewicht = request.POST.get('gewicht')
        eintrag.gewicht = gewicht if gewicht else None
        eintrag.alter_geschaetzt = request.POST.get('alter_geschaetzt', '')
        eintrag.jagdart = request.POST.get('jagdart', '')
        entfernung = request.POST.get('entfernung')
        eintrag.entfernung = entfernung if entfernung else None
        eintrag.notizen = request.POST.get('notizen', '')
        eintrag.wetter = request.POST.get('wetter', '')
        temperatur = request.POST.get('temperatur')
        eintrag.temperatur = temperatur if temperatur else None
        eintrag.trophaee = request.POST.get('trophaee') == 'on'
        eintrag.save()
        messages.success(request, 'Eintrag wurde aktualisiert.')
        return redirect('eintrag_detail', pk=eintrag.pk)
    
    heute = date.today().strftime('%Y-%m-%d')
    context = {
        'eintrag': eintrag,
        'WILDART_CHOICES': JagdLog.WILDART_CHOICES,
        'GESCHLECHT_CHOICES': JagdLog.GESCHLECHT_CHOICES,
        'heute': heute,
        'reviere': reviere,
        'hochsitze': hochsitze,
        'waffen': waffen,
    }
    return render(request, 'jagd/eintrag_form.html', context)

@login_required
def eintrag_loeschen(request, pk):
    eintrag = get_object_or_404(JagdLog, pk=pk, user=request.user)
    if request.method == 'POST':
        eintrag.delete()
        messages.success(request, 'Eintrag wurde geloescht.')
        return redirect('dashboard')
    return render(request, 'jagd/eintrag_confirm_delete.html', {'eintrag': eintrag})

@login_required
def liste(request):
    eintraege = JagdLog.objects.filter(user=request.user)
    
    wildart_filter = request.GET.get('wildart', '')
    revier_filter = request.GET.get('revier', '')
    jahr_filter = request.GET.get('jahr', '')
    sort = request.GET.get('sort', '-datum')
    
    if wildart_filter:
        eintraege = eintraege.filter(wildart=wildart_filter)
    if revier_filter:
        eintraege = eintraege.filter(revier_ref_id=revier_filter)
    if jahr_filter:
        eintraege = eintraege.filter(datum__year=jahr_filter)
    
    if sort in ['-datum', 'datum', 'wildart', '-gewicht']:
        eintraege = eintraege.order_by(sort)
    else:
        eintraege = eintraege.order_by('-datum')
    
    reviere = Revier.objects.filter(user=request.user)
    jahre = JagdLog.objects.filter(user=request.user).dates('datum', 'year', order='DESC')
    jahre = [d.year for d in jahre]
    
    context = {
        'eintraege': eintraege,
        'reviere': reviere,
        'jahre': jahre,
    }
    return render(request, 'jagd/liste.html', context)

@login_required
def liste_detailliert(request):
    """Detaillierte Tabelle mit allen Datenbankfeldern"""
    eintraege = JagdLog.objects.filter(user=request.user).select_related('revier_ref', 'hochsitz_ref').order_by('-datum')
    
    # Wildart-Labels für Anzeige
    wildart_labels = {}
    for group, choices in JagdLog.WILDART_CHOICES:
        for value, label in choices:
            wildart_labels[value] = label
    
    context = {
        'eintraege': eintraege,
        'wildart_labels': wildart_labels,
    }
    return render(request, 'jagd/liste_detailliert.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Konto erstellt! Du kannst dich jetzt anmelden.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# ==================== BENUTZERVERWALTUNG ====================

@login_required
@user_passes_test(superuser_required)
def benutzer_liste(request):
    """Liste aller Benutzer (nur für Superuser)"""
    benutzer = User.objects.all().order_by('username')
    # Anzahl Einträge pro Benutzer
    benutzer_stats = []
    for user in benutzer:
        eintraege_count = JagdLog.objects.filter(user=user).count()
        benutzer_stats.append({
            'user': user,
            'eintraege_count': eintraege_count,
        })
    return render(request, 'jagd/benutzer_liste.html', {'benutzer_stats': benutzer_stats})


@login_required
@user_passes_test(superuser_required)
def benutzer_neu(request):
    """Neuen Benutzer erstellen (nur für Superuser)"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        if not username:
            messages.error(request, 'Benutzername ist erforderlich.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Dieser Benutzername existiert bereits.')
        elif len(password) < 8:
            messages.error(request, 'Passwort muss mindestens 8 Zeichen haben.')
        elif password != password2:
            messages.error(request, 'Passwörter stimmen nicht überein.')
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_superuser = is_superuser
            user.is_staff = is_superuser
            user.save()
            messages.success(request, f'Benutzer "{username}" wurde erstellt.')
            return redirect('benutzer_liste')
    
    return render(request, 'jagd/benutzer_form.html', {'aktion': 'Neuer Benutzer'})


@login_required
@user_passes_test(superuser_required)
def benutzer_bearbeiten(request, pk):
    """Benutzer bearbeiten (nur für Superuser)"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        is_superuser = request.POST.get('is_superuser') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        if not username:
            messages.error(request, 'Benutzername ist erforderlich.')
        elif User.objects.filter(username=username).exclude(pk=pk).exists():
            messages.error(request, 'Dieser Benutzername existiert bereits.')
        else:
            user.username = username
            user.is_superuser = is_superuser
            user.is_staff = is_superuser
            user.is_active = is_active
            
            # Passwort nur ändern wenn ausgefüllt
            if password:
                if len(password) < 8:
                    messages.error(request, 'Passwort muss mindestens 8 Zeichen haben.')
                    return render(request, 'jagd/benutzer_form.html', {'aktion': 'Benutzer bearbeiten', 'benutzer': user})
                elif password != password2:
                    messages.error(request, 'Passwörter stimmen nicht überein.')
                    return render(request, 'jagd/benutzer_form.html', {'aktion': 'Benutzer bearbeiten', 'benutzer': user})
                else:
                    user.set_password(password)
            
            user.save()
            messages.success(request, f'Benutzer "{username}" wurde aktualisiert.')
            return redirect('benutzer_liste')
    
    return render(request, 'jagd/benutzer_form.html', {'aktion': 'Benutzer bearbeiten', 'benutzer': user})


@login_required
@user_passes_test(superuser_required)
def benutzer_loeschen(request, pk):
    """Benutzer löschen (nur für Superuser)"""
    user = get_object_or_404(User, pk=pk)
    
    # Sich selbst nicht löschen können
    if user == request.user:
        messages.error(request, 'Du kannst dich nicht selbst löschen.')
        return redirect('benutzer_liste')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Benutzer "{username}" wurde gelöscht.')
        return redirect('benutzer_liste')
    
    eintraege_count = JagdLog.objects.filter(user=user).count()
    return render(request, 'jagd/benutzer_confirm_delete.html', {'benutzer': user, 'eintraege_count': eintraege_count})


# ==================== REVIER-VERWALTUNG ====================

@login_required
def revier_liste(request):
    """Liste aller Reviere des Benutzers"""
    reviere = Revier.objects.filter(user=request.user).annotate(
        hochsitz_count=Count('hochsitze')
    )
    return render(request, 'jagd/revier_liste.html', {'reviere': reviere})


@login_required
def revier_neu(request):
    """Neues Revier erstellen"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        beschreibung = request.POST.get('beschreibung', '').strip()
        groesse_ha = request.POST.get('groesse_ha', '').strip()
        
        if not name:
            messages.error(request, 'Name ist erforderlich.')
        elif Revier.objects.filter(user=request.user, name=name).exists():
            messages.error(request, 'Ein Revier mit diesem Namen existiert bereits.')
        else:
            revier = Revier(user=request.user, name=name, beschreibung=beschreibung)
            if groesse_ha:
                revier.groesse_ha = groesse_ha
            revier.save()
            messages.success(request, f'Revier "{name}" wurde erstellt.')
            return redirect('revier_liste')
    
    return render(request, 'jagd/revier_form.html', {'aktion': 'Neues Revier'})


@login_required
def revier_bearbeiten(request, pk):
    """Revier bearbeiten"""
    revier = get_object_or_404(Revier, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        beschreibung = request.POST.get('beschreibung', '').strip()
        groesse_ha = request.POST.get('groesse_ha', '').strip()
        
        if not name:
            messages.error(request, 'Name ist erforderlich.')
        elif Revier.objects.filter(user=request.user, name=name).exclude(pk=pk).exists():
            messages.error(request, 'Ein Revier mit diesem Namen existiert bereits.')
        else:
            revier.name = name
            revier.beschreibung = beschreibung
            revier.groesse_ha = groesse_ha if groesse_ha else None
            revier.save()
            messages.success(request, f'Revier "{name}" wurde aktualisiert.')
            return redirect('revier_liste')
    
    return render(request, 'jagd/revier_form.html', {'aktion': 'Revier bearbeiten', 'revier': revier})


@login_required
def revier_loeschen(request, pk):
    """Revier löschen"""
    revier = get_object_or_404(Revier, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = revier.name
        revier.delete()
        messages.success(request, f'Revier "{name}" wurde gelöscht.')
        return redirect('revier_liste')
    
    hochsitz_count = revier.hochsitze.count()
    return render(request, 'jagd/revier_confirm_delete.html', {'revier': revier, 'hochsitz_count': hochsitz_count})


# ==================== HOCHSITZ-VERWALTUNG ====================

@login_required
def hochsitz_liste(request, revier_pk=None):
    """Liste aller Hochsitze (optional gefiltert nach Revier)"""
    hochsitze = Hochsitz.objects.filter(user=request.user).select_related('revier')
    reviere = Revier.objects.filter(user=request.user)
    
    revier_filter = None
    if revier_pk:
        revier_filter = get_object_or_404(Revier, pk=revier_pk, user=request.user)
        hochsitze = hochsitze.filter(revier=revier_filter)
    
    zustand_filter = request.GET.get('zustand', '')
    if zustand_filter:
        hochsitze = hochsitze.filter(zustand=zustand_filter)
    
    return render(request, 'jagd/hochsitz_liste.html', {
        'hochsitze': hochsitze,
        'reviere': reviere,
        'revier_filter': revier_filter,
        'zustand_filter': zustand_filter,
        'ZUSTAND_CHOICES': Hochsitz.ZUSTAND_CHOICES,
    })


@login_required
def hochsitz_neu(request, revier_pk=None):
    """Neuen Hochsitz erstellen"""
    reviere = Revier.objects.filter(user=request.user)
    
    if not reviere.exists():
        messages.warning(request, 'Bitte erstelle zuerst ein Revier.')
        return redirect('revier_neu')
    
    vorausgewaehltes_revier = None
    if revier_pk:
        vorausgewaehltes_revier = get_object_or_404(Revier, pk=revier_pk, user=request.user)
    
    if request.method == 'POST':
        revier_id = request.POST.get('revier')
        name = request.POST.get('name', '').strip()
        typ = request.POST.get('typ', 'kanzel')
        beschreibung = request.POST.get('beschreibung', '').strip()
        gps_latitude = request.POST.get('gps_latitude', '').strip()
        gps_longitude = request.POST.get('gps_longitude', '').strip()
        zustand = request.POST.get('zustand', 'gut')
        baujahr = request.POST.get('baujahr', '').strip()
        letzte_kontrolle = request.POST.get('letzte_kontrolle', '').strip()
        notizen = request.POST.get('notizen', '').strip()
        aktiv = request.POST.get('aktiv') == 'on'
        
        if not name:
            messages.error(request, 'Name ist erforderlich.')
        elif not revier_id:
            messages.error(request, 'Revier ist erforderlich.')
        else:
            revier = get_object_or_404(Revier, pk=revier_id, user=request.user)
            hochsitz = Hochsitz(
                user=request.user,
                revier=revier,
                name=name,
                typ=typ,
                beschreibung=beschreibung,
                zustand=zustand,
                notizen=notizen,
                aktiv=aktiv,
            )
            if gps_latitude:
                hochsitz.gps_latitude = gps_latitude
            if gps_longitude:
                hochsitz.gps_longitude = gps_longitude
            if baujahr:
                hochsitz.baujahr = baujahr
            if letzte_kontrolle:
                hochsitz.letzte_kontrolle = letzte_kontrolle
            hochsitz.save()
            messages.success(request, f'Hochsitz "{name}" wurde erstellt.')
            return redirect('hochsitz_liste')
    
    return render(request, 'jagd/hochsitz_form.html', {
        'aktion': 'Neuer Hochsitz',
        'reviere': reviere,
        'vorausgewaehltes_revier': vorausgewaehltes_revier,
        'TYP_CHOICES': Hochsitz.TYP_CHOICES,
        'ZUSTAND_CHOICES': Hochsitz.ZUSTAND_CHOICES,
    })


@login_required
def hochsitz_detail(request, pk):
    """Hochsitz-Details anzeigen"""
    hochsitz = get_object_or_404(Hochsitz, pk=pk, user=request.user)
    return render(request, 'jagd/hochsitz_detail.html', {'hochsitz': hochsitz})


@login_required
def hochsitz_bearbeiten(request, pk):
    """Hochsitz bearbeiten"""
    hochsitz = get_object_or_404(Hochsitz, pk=pk, user=request.user)
    reviere = Revier.objects.filter(user=request.user)
    
    if request.method == 'POST':
        revier_id = request.POST.get('revier')
        name = request.POST.get('name', '').strip()
        typ = request.POST.get('typ', 'kanzel')
        beschreibung = request.POST.get('beschreibung', '').strip()
        gps_latitude = request.POST.get('gps_latitude', '').strip()
        gps_longitude = request.POST.get('gps_longitude', '').strip()
        zustand = request.POST.get('zustand', 'gut')
        baujahr = request.POST.get('baujahr', '').strip()
        letzte_kontrolle = request.POST.get('letzte_kontrolle', '').strip()
        notizen = request.POST.get('notizen', '').strip()
        aktiv = request.POST.get('aktiv') == 'on'
        
        if not name:
            messages.error(request, 'Name ist erforderlich.')
        elif not revier_id:
            messages.error(request, 'Revier ist erforderlich.')
        else:
            revier = get_object_or_404(Revier, pk=revier_id, user=request.user)
            hochsitz.revier = revier
            hochsitz.name = name
            hochsitz.typ = typ
            hochsitz.beschreibung = beschreibung
            hochsitz.gps_latitude = gps_latitude if gps_latitude else None
            hochsitz.gps_longitude = gps_longitude if gps_longitude else None
            hochsitz.zustand = zustand
            hochsitz.baujahr = baujahr if baujahr else None
            hochsitz.letzte_kontrolle = letzte_kontrolle if letzte_kontrolle else None
            hochsitz.notizen = notizen
            hochsitz.aktiv = aktiv
            hochsitz.save()
            messages.success(request, f'Hochsitz "{name}" wurde aktualisiert.')
            return redirect('hochsitz_liste')
    
    return render(request, 'jagd/hochsitz_form.html', {
        'aktion': 'Hochsitz bearbeiten',
        'hochsitz': hochsitz,
        'reviere': reviere,
        'TYP_CHOICES': Hochsitz.TYP_CHOICES,
        'ZUSTAND_CHOICES': Hochsitz.ZUSTAND_CHOICES,
    })


@login_required
def hochsitz_loeschen(request, pk):
    """Hochsitz löschen"""
    hochsitz = get_object_or_404(Hochsitz, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = hochsitz.name
        hochsitz.delete()
        messages.success(request, f'Hochsitz "{name}" wurde gelöscht.')
        return redirect('hochsitz_liste')
    
    return render(request, 'jagd/hochsitz_confirm_delete.html', {'hochsitz': hochsitz})


# ==================== WAFFENVERWALTUNG ====================

from .models import Waffe

@login_required
def waffe_liste(request):
    """Liste aller Waffen des Benutzers"""
    waffen = Waffe.objects.filter(user=request.user)
    return render(request, 'jagd/waffe_liste.html', {'waffen': waffen})


@login_required
def waffe_neu(request):
    """Neue Waffe anlegen"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        typ = request.POST.get('typ', 'buechse')
        hersteller = request.POST.get('hersteller', '').strip()
        modell = request.POST.get('modell', '').strip()
        kaliber = request.POST.get('kaliber', '').strip()
        seriennummer = request.POST.get('seriennummer', '').strip()
        kaufdatum = request.POST.get('kaufdatum', '').strip()
        wbk_nummer = request.POST.get('wbk_nummer', '').strip()
        notizen = request.POST.get('notizen', '').strip()
        aktiv = request.POST.get('aktiv') == 'on'
        
        if not name:
            messages.error(request, 'Bezeichnung ist erforderlich.')
        elif not kaliber:
            messages.error(request, 'Kaliber ist erforderlich.')
        else:
            Waffe.objects.create(
                user=request.user,
                name=name,
                typ=typ,
                hersteller=hersteller,
                modell=modell,
                kaliber=kaliber,
                seriennummer=seriennummer,
                kaufdatum=kaufdatum if kaufdatum else None,
                wbk_nummer=wbk_nummer,
                notizen=notizen,
                aktiv=aktiv,
            )
            messages.success(request, f'Waffe "{name}" wurde angelegt.')
            return redirect('waffe_liste')
    
    return render(request, 'jagd/waffe_form.html', {
        'aktion': 'Neue Waffe anlegen',
        'TYP_CHOICES': Waffe.TYP_CHOICES,
    })


@login_required
def waffe_bearbeiten(request, pk):
    """Waffe bearbeiten"""
    waffe = get_object_or_404(Waffe, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        typ = request.POST.get('typ', 'buechse')
        hersteller = request.POST.get('hersteller', '').strip()
        modell = request.POST.get('modell', '').strip()
        kaliber = request.POST.get('kaliber', '').strip()
        seriennummer = request.POST.get('seriennummer', '').strip()
        kaufdatum = request.POST.get('kaufdatum', '').strip()
        wbk_nummer = request.POST.get('wbk_nummer', '').strip()
        notizen = request.POST.get('notizen', '').strip()
        aktiv = request.POST.get('aktiv') == 'on'
        
        if not name:
            messages.error(request, 'Bezeichnung ist erforderlich.')
        elif not kaliber:
            messages.error(request, 'Kaliber ist erforderlich.')
        else:
            waffe.name = name
            waffe.typ = typ
            waffe.hersteller = hersteller
            waffe.modell = modell
            waffe.kaliber = kaliber
            waffe.seriennummer = seriennummer
            waffe.kaufdatum = kaufdatum if kaufdatum else None
            waffe.wbk_nummer = wbk_nummer
            waffe.notizen = notizen
            waffe.aktiv = aktiv
            waffe.save()
            messages.success(request, f'Waffe "{name}" wurde aktualisiert.')
            return redirect('waffe_liste')
    
    return render(request, 'jagd/waffe_form.html', {
        'aktion': 'Waffe bearbeiten',
        'waffe': waffe,
        'TYP_CHOICES': Waffe.TYP_CHOICES,
    })


@login_required
def waffe_loeschen(request, pk):
    """Waffe löschen"""
    waffe = get_object_or_404(Waffe, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = waffe.name
        waffe.delete()
        messages.success(request, f'Waffe "{name}" wurde gelöscht.')
        return redirect('waffe_liste')
    
    return render(request, 'jagd/waffe_confirm_delete.html', {'waffe': waffe})
