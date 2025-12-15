from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Count
from datetime import date, timedelta
from .models import JagdLog

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
    
    saison_stats = {
        'gesamt': saison_eintraege.count(),
        'rehwild': saison_eintraege.filter(wildart__in=['rehbock', 'ricke', 'rehkitz']).count(),
        'schwarzwild': saison_eintraege.filter(wildart='schwarzwild').count(),
        'niederwild': saison_eintraege.filter(wildart__in=['hase', 'wildkaninchen', 'fasan', 'rebhuhn', 'wildente', 'wildgans', 'wildtaube']).count(),
        'raubwild': saison_eintraege.filter(wildart__in=['fuchs', 'dachs', 'marder', 'waschbaer', 'marderhund']).count(),
    }
    
    letzte_eintraege = eintraege[:5]
    wildarten_stats = saison_eintraege.values('wildart').annotate(count=Count('wildart')).order_by('-count')[:5]
    reviere = saison_eintraege.exclude(revier='').values('revier').annotate(count=Count('revier')).order_by('-count')[:5]
    
    context = {
        'saison_start': saison_start,
        'saison_ende': saison_ende,
        'saison_stats': saison_stats,
        'letzte_eintraege': letzte_eintraege,
        'wildarten_stats': wildarten_stats,
        'reviere': reviere,
    }
    return render(request, 'jagd/dashboard.html', context)

@login_required
def eintrag_neu(request):
    if request.method == 'POST':
        eintrag = JagdLog(user=request.user)
        eintrag.wildart = request.POST.get('wildart', 'rehbock')
        eintrag.datum = request.POST.get('datum', date.today())
        uhrzeit = request.POST.get('uhrzeit')
        if uhrzeit:
            eintrag.uhrzeit = uhrzeit
        eintrag.revier = request.POST.get('revier', '')
        eintrag.geschlecht = request.POST.get('geschlecht', 'u')
        gewicht = request.POST.get('gewicht')
        if gewicht:
            eintrag.gewicht = gewicht
        eintrag.alter_geschaetzt = request.POST.get('alter_geschaetzt', '')
        eintrag.jagdart = request.POST.get('jagdart', '')
        eintrag.waffe = request.POST.get('waffe', '')
        entfernung = request.POST.get('entfernung')
        if entfernung:
            eintrag.entfernung = entfernung
        eintrag.notizen = request.POST.get('notizen', '')
        eintrag.wetter = request.POST.get('wetter', '')
        temperatur = request.POST.get('temperatur')
        if temperatur:
            eintrag.temperatur = temperatur
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
    }
    return render(request, 'jagd/eintrag_form.html', context)

@login_required
def eintrag_detail(request, pk):
    eintrag = get_object_or_404(JagdLog, pk=pk, user=request.user)
    return render(request, 'jagd/eintrag_detail.html', {'eintrag': eintrag})

@login_required
def eintrag_bearbeiten(request, pk):
    eintrag = get_object_or_404(JagdLog, pk=pk, user=request.user)
    if request.method == 'POST':
        eintrag.wildart = request.POST.get('wildart', eintrag.wildart)
        eintrag.datum = request.POST.get('datum', eintrag.datum)
        uhrzeit = request.POST.get('uhrzeit')
        eintrag.uhrzeit = uhrzeit if uhrzeit else None
        eintrag.revier = request.POST.get('revier', '')
        eintrag.geschlecht = request.POST.get('geschlecht', 'u')
        gewicht = request.POST.get('gewicht')
        eintrag.gewicht = gewicht if gewicht else None
        eintrag.alter_geschaetzt = request.POST.get('alter_geschaetzt', '')
        eintrag.jagdart = request.POST.get('jagdart', '')
        eintrag.waffe = request.POST.get('waffe', '')
        entfernung = request.POST.get('entfernung')
        eintrag.entfernung = entfernung if entfernung else None
        eintrag.notizen = request.POST.get('notizen', '')
        eintrag.wetter = request.POST.get('wetter', '')
        temperatur = request.POST.get('temperatur')
        eintrag.temperatur = temperatur if temperatur else None
        eintrag.save()
        messages.success(request, 'Eintrag wurde aktualisiert.')
        return redirect('eintrag_detail', pk=eintrag.pk)
    
    context = {
        'eintrag': eintrag,
        'WILDART_CHOICES': JagdLog.WILDART_CHOICES,
        'GESCHLECHT_CHOICES': JagdLog.GESCHLECHT_CHOICES,
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
        eintraege = eintraege.filter(revier=revier_filter)
    if jahr_filter:
        eintraege = eintraege.filter(datum__year=jahr_filter)
    
    if sort in ['-datum', 'datum', 'wildart', '-gewicht']:
        eintraege = eintraege.order_by(sort)
    else:
        eintraege = eintraege.order_by('-datum')
    
    reviere = JagdLog.objects.filter(user=request.user).exclude(revier='').values_list('revier', flat=True).distinct()
    jahre = JagdLog.objects.filter(user=request.user).dates('datum', 'year', order='DESC')
    jahre = [d.year for d in jahre]
    
    context = {
        'eintraege': eintraege,
        'reviere': reviere,
        'jahre': jahre,
    }
    return render(request, 'jagd/liste.html', context)

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
