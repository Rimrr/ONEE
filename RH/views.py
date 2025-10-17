# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import RH
from .forms import RHForm

def liste_rh(request):
    rhs = RH.objects.all()
    return render(request, 'rh/liste_rh.html', {'rhs': rhs})

def ajouter_rh(request):
    if request.method == 'POST':
        form = RHForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_rh')
    else:
        form = RHForm()
    return render(request, 'rh/rh_form.html', {'form': form})

def modifier_rh(request, rh_id):
    rh = get_object_or_404(RH, id=rh_id)
    if request.method == 'POST':
        form = RHForm(request.POST, instance=rh)
        if form.is_valid():
            form.save()
            return redirect('liste_rh')
    else:
        form = RHForm(instance=rh)
    return render(request, 'rh/rh_form.html', {'form': form})

def supprimer_rh(request, rh_id):
    rh = get_object_or_404(RH, id=rh_id)
    if request.method == 'POST':
        rh.delete()
        return redirect('liste_rh')
    return render(request, 'rh/supprimer_rh.html', {'rh': rh})


from django.contrib import messages
from .models import RH
from .forms import RHLoginForm

from django.shortcuts import redirect, render
from django.contrib import messages
from .models import RH
from .forms import RHLoginForm

def rh_login_view(request):
    if request.method == 'POST':
        form = RHLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mot_de_passe = form.cleaned_data['mot_de_passe']

            try:
                rh = RH.objects.get(email=email)

                if rh.check_mot_de_passe(mot_de_passe):
                    # Connexion réussie
                    request.session['rh_id'] = rh.id

                    # ➜ Redirection selon le status
                    if rh.status == 0:
                        return redirect('dashboard_rh')   # crée cette URL / vue
                    else:  # status == 1
                        return redirect('rhe_dashboard')        # admin / superviseur
                else:
                    messages.error(request, "Mot de passe incorrect.")
            except RH.DoesNotExist:
                messages.error(request, "Aucun compte RH avec cet email.")
    else:
        form = RHLoginForm()

    return render(request, 'rh/login.html', {'form': form})

# views.py

from django.shortcuts import render
from django.db.models import Count
from .models import Offre, Candidature

def dashboard_rh(request):
    offres_count = Offre.objects.count()
    candidature_count = Candidature.objects.count()  # ✅ ici

    candidatures_statut = (
        Candidature.objects.values('statut')
        .annotate(total=Count('id'))
    )

    offres_categorie = (
        Offre.objects.values('categorie')
        .annotate(total=Count('id'))
    )

    context = {
        'offres_count': offres_count,
        'candidature_count': candidature_count,  # ✅ ajouté ici
        'candidatures_statut': list(candidatures_statut),
        'offres_categorie': list(offres_categorie),
    }


    return render(request, 'rh/dashboard.html',context)


def rh_logout_view(request):
    if 'rh_id' in request.session:
        del request.session['rh_id']
    return redirect('rh_login')

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Offre
from .forms import OffreForm

def liste_offres(request):
    filtre = request.GET.get('filtre')  # "active", "archive" ou None

    if filtre == 'active':
        offres = Offre.objects.filter(date_expiration__gte=timezone.now().date())
    elif filtre == 'archive':
        offres = Offre.objects.filter(date_expiration__lt=timezone.now().date())
    else:
        offres = Offre.objects.all()
    return render(request, 'offres/liste.html', {'offres': offres})

def creer_offre(request):
    if request.method == 'POST':
        form = OffreForm(request.POST)
        if form.is_valid():
            offre = form.save()
            return redirect('liste_offres')
    else:
        form = OffreForm()
    return render(request, 'offres/formulaire.html', {'form': form, 'entreprise': 'ONEE'})

def modifier_offre(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if request.method == 'POST':
        form = OffreForm(request.POST, instance=offre)
        if form.is_valid():
            form.save()
            return redirect('liste_offres')
    else:
        form = OffreForm(instance=offre)
    return render(request, 'offres/formulaire.html', {'form': form, 'entreprise': 'ONEE'})

from django.shortcuts import get_object_or_404, redirect, render
from .models import Offre

def supprimer_offre(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if request.method == 'POST':
        offre.delete()
        return redirect('liste_offres')  # adapter selon ta vue liste
    return render(request, 'offres/supprimer_offre.html', {'offre': offre})


from django.shortcuts import render, redirect
from .models import Candidat
from .forms import CandidatRegisterForm, CandidatLoginForm
from django.contrib import messages

def candidat_register_view(request):
    if request.method == 'POST':
        form = CandidatRegisterForm(request.POST)
        if form.is_valid():
            candidat = form.save(commit=False)
            candidat.set_mot_de_passe(form.cleaned_data['mot_de_passe'])
            candidat.save()
            messages.success(request, "Compte créé avec succès. Connectez-vous.")
            return redirect('candidat_login')
    else:
        form = CandidatRegisterForm()
    return render(request, 'candidat/register.html', {'form': form})

def candidat_login_view(request):
    if request.method == 'POST':
        form = CandidatLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mot_de_passe = form.cleaned_data['mot_de_passe']
            try:
                candidat = Candidat.objects.get(email=email)
                if candidat.check_mot_de_passe(mot_de_passe):
                    request.session['candidat_id'] = candidat.id
                    return redirect('candidat_dashboard')
                else:
                    messages.error(request, "Mot de passe incorrect.")
            except Candidat.DoesNotExist:
                messages.error(request, "Aucun compte avec cet email.")
    else:
        form = CandidatLoginForm()
    return render(request, 'candidat/login.html', {'form': form})
from django.shortcuts import render, redirect, get_object_or_404
from .models import Candidat, Candidature
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Count

def candidat_dashboard(request):
    candidat_id = request.session.get('candidat_id')
    if not candidat_id:
        return redirect('candidat_login')  # Redirige si pas connecté

    candidat = get_object_or_404(Candidat, id=candidat_id)

    # Total candidatures et entretiens
    total_candidatures = Candidature.objects.filter(candidat=candidat).count()
    entretiens = Candidature.objects.filter(candidat=candidat, statut__in=['concours_Ecrit', 'concours_Oral']).count()
    offres_sauvegardees = 0  # À implémenter selon modèle

    # Statistiques graphiques (30 derniers jours)
    date_limite = now() - timedelta(days=30)
    candidatures_recentes = (
        Candidature.objects
        .filter(candidat=candidat, date_postulation__gte=date_limite)
        .extra({'date': "date(date_postulation)"})
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    dates = [item['date'].strftime('%d %b') for item in candidatures_recentes]
    counts = [item['count'] for item in candidatures_recentes]

    # Diagramme circulaire : répartition des statuts
    statuts = (
        Candidature.objects
        .filter(candidat=candidat)
        .values('statut')
        .annotate(count=Count('id'))
    )
    statut_labels = [dict(Candidature.STATUTS).get(item['statut'], item['statut']) for item in statuts]
    statut_data = [item['count'] for item in statuts]

    # Candidatures récentes
    recent_applications = (
        Candidature.objects
        .filter(candidat=candidat)
        .select_related('offre')
        .order_by('-date_postulation')[:5]
    )

    # Exemple d’évolution (tu peux remplacer par un vrai calcul)
    evolution_candidatures = 10
    evolution_entretiens = -5

    # Contexte global
    context = {
        'candidat': candidat,
        'total_candidatures': total_candidatures,
        'entretiens': entretiens,
        'offres_sauvegardees': offres_sauvegardees,
        'dates_json': dates,
        'counts_json': counts,
        'statut_labels_json': statut_labels,
        'statut_data_json': statut_data,
        'recent_applications': recent_applications,
        'evolution_candidatures': evolution_candidatures,
        'evolution_entretiens': evolution_entretiens,
        'evolution_candidatures_abs': abs(evolution_candidatures),
        'evolution_entretiens_abs': abs(evolution_entretiens),
    }

    return render(request, 'candidat/dashboard.html', context)

def candidat_logout_view(request):
    request.session.flush()
    return redirect('candidat_login')


from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import Offre
import json
from datetime import date

def rhe_dashboard(request):
    # ➜ KPI simples
    total_offres = Offre.objects.count()
    offres_actives = Offre.objects.filter(date_expiration__gte=date.today()).count()
    offres_expirees = total_offres - offres_actives

    kpis = [
        {"label": "Offres totales", "value": total_offres},
        {"label": "Actives",        "value": offres_actives},
        {"label": "Expirées",       "value": offres_expirees},
    ]

    # ➜ Offres publiées par mois (12 derniers mois)
    qs_months = (
        Offre.objects
        .filter(date_publication__year=date.today().year)
        .annotate(month=TruncMonth("date_publication"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )
    labels_months = [m["month"].strftime("%b") for m in qs_months]
    data_months   = [m["total"] for m in qs_months]

    # ➜ Répartition par catégorie
    qs_cats = (
        Offre.objects
        .values("categorie")
        .annotate(total=Count("id"))
        .order_by()
    )
    labels_cats = [c["categorie"].title().replace("_", " ") for c in qs_cats]
    data_cats   = [c["total"] for c in qs_cats]

    context = {
        "kpis": kpis,
        "labels_months": json.dumps(labels_months),
        "data_months":   json.dumps(data_months),
        "labels_cats":   json.dumps(labels_cats),
        "data_cats":     json.dumps(data_cats),
    }
    return render(request, "dashboard.html", context)
# views.py
from django.shortcuts import render
from django.utils import timezone
from .models import Offre

def liste_offres_candidat(request):
    today = timezone.now().date()
    offres = Offre.objects.filter(date_expiration__gte=today).order_by('-date_publication')

    return render(request, 'candidat/liste_offres.html', {'offres': offres})
def liste_offres_candidat(request):
    today = timezone.now().date()
    offres = Offre.objects.filter(date_expiration__gte=today)

    categorie = request.GET.get('categorie')
    contrat = request.GET.get('contrat')

    if categorie:
        offres = offres.filter(categorie=categorie)

    if contrat:
        offres = offres.filter(type_contrat=contrat)

    context = {
        'offres': offres,
        'categorie': categorie,
        'contrat': contrat
    }
    return render(request, 'candidat/liste_offres.html', context)
def detail_offre(request, id):
    offre = get_object_or_404(Offre, id=id)
    candidature_existante = False

    candidat_id = request.session.get('candidat_id')
    if candidat_id:
        try:
            candidat = Candidat.objects.get(id=candidat_id)
            candidature_existante = Candidature.objects.filter(candidat=candidat, offre=offre).exists()
        except Candidat.DoesNotExist:
            pass

    return render(request, 'candidat/detail_offre.html', {
        'offre': offre,
        'deja_postule': candidature_existante
    })

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Offre, Candidature, Candidat
from .forms import CandidatureForm
def postuler_offre(request, id):
    candidat_id = request.session.get('candidat_id')

    if not candidat_id:
        return redirect('candidat_login')

    candidat = get_object_or_404(Candidat, id=candidat_id)
    offre = get_object_or_404(Offre, id=id)

    # Empêcher de postuler deux fois
    if Candidature.objects.filter(candidat=candidat, offre=offre).exists():
        messages.warning(request, "Vous avez déjà postulé à cette offre.")
        return redirect('detail_offre', id=offre.id)

    if request.method == 'POST':
        form = CandidatureForm(request.POST, request.FILES)
        if form.is_valid():
            candidature = form.save(commit=False)
            candidature.candidat = candidat
            candidature.offre = offre
            candidature.save()
            messages.success(request, "Votre candidature a été envoyée avec succès.")
            return redirect('candidat_dashboard')
    else:
        form = CandidatureForm()

    return render(request, 'candidat/postuler.html', {
        'form': form,
        'offre': offre
    })



from django.shortcuts import render, redirect, get_object_or_404
from .models import Candidat, Candidature

from django.core.paginator import Paginator

def mes_candidatures(request):
    candidat_id = request.session.get('candidat_id')
    if not candidat_id:
        return redirect('candidat_login')

    candidat = get_object_or_404(Candidat, id=candidat_id)
    candidature_list = Candidature.objects.filter(candidat=candidat).select_related('offre').order_by('-date_postulation')

    paginator = Paginator(candidature_list, 10)  # 10 par page
    page = request.GET.get('page')
    candidatures = paginator.get_page(page)

    return render(request, 'candidat/mes_candidatures.html', {
        'candidat': candidat,
        'candidatures': candidatures,
    })

from django.shortcuts import get_object_or_404

def detail_offrerh(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id)
    return render(request, 'offres/detail_offre.html', {'offre': offre})

# views.py
from django.shortcuts import render
from .models import Offre
def detail_offrerh(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id)
    return render(request, 'offres/detail_offre_rh.html', {'offre': offre})
# views.py
# views.py
from django.shortcuts import render, get_object_or_404
from .models import Offre, Candidature

def candidatures_par_offre(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id)
    statut_filtre = request.GET.get('statut')
    
    if statut_filtre:
        candidatures = Candidature.objects.filter(offre=offre, statut=statut_filtre)
    else:
        candidatures = Candidature.objects.filter(offre=offre)

    return render(request, 'offres/candidatures_par_offre.html', {
        'offre': offre,
        'candidatures': candidatures
    })
  

from django.shortcuts import redirect
from .models import Candidature

def modifier_statut_candidature(request, candidature_id):
    candidature = Candidature.objects.get(id=candidature_id)
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        candidature.statut = nouveau_statut
        candidature.save()
    return redirect('candidatures_par_offre', offre_id=candidature.offre.id)
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Offre
import io
from django.shortcuts import get_object_or_404

def telecharger_offre_pdf(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id)
    template = get_template('offres/pdf_template.html')
    html = template.render({'offre': offre})

    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="offre_{offre_id}.pdf"'
        return response
    else:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)


from django.shortcuts import render, get_object_or_404
from .models import Offre, Candidature

def liste_offre(request):
    offres = Offre.objects.all()
    return render(request, 'rh/offres_list.html', {'offres': offres})

from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

@require_http_methods(["GET", "POST"])
def candidats_pour_offre(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id)

    if request.method == 'POST':
        candidature_id = request.POST.get('candidature_id')
        new_statut = request.POST.get('statut')
        if candidature_id and new_statut:
            candidature = get_object_or_404(Candidature, id=candidature_id, offre=offre)
            candidature.statut = new_statut
            candidature.save()
        return redirect('candidats_par_offre', offre_id=offre_id)

    candidatures = Candidature.objects.filter(offre=offre).select_related('candidat')
    return render(request, 'rh/candidats_par_offre.html', {
        'offre': offre,
        'candidatures': candidatures,
        'STATUTS': Candidature.STATUTS,
    })


from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


# views.py

from django.shortcuts import render, get_object_or_404
from .models import Candidature

def detail_candidature(request, candidature_id):
    candidature = get_object_or_404(Candidature, id=candidature_id)
    return render(request, 'detail_candidature.html', {'candidature': candidature})


import csv
from django.http import HttpResponse
from datetime import datetime

def export_candidatures(request, offre_id):
    # Récupérer l'offre et les candidatures associées
    offre = Offre.objects.get(pk=offre_id)
    candidatures = Candidature.objects.filter(offre=offre).select_related('candidat')
    
    # Créer la réponse HTTP avec le bon header pour un fichier CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="candidatures_{offre.titre}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Écrire l'en-tête du CSV
    writer.writerow([
        'ID Candidature', 'Date Postulation', 'Statut', 
        'Nom', 'Prénom', 'Email', 'Téléphone', 'Date Naissance', 'Sexe',
        'Adresse', 'Ville', 'Pays', 'Titre Profil', 
        'Niveau Étude', 'Années Expérience', 'Permis',
        'Lettre Motivation', 'CV', 'CIN', 'Diplôme',
        'LinkedIn', 'GitHub', 'Résumé Professionnel'
    ])
    
    # Écrire les données pour chaque candidature
    for c in candidatures:
        writer.writerow([
            c.id, 
            c.date_postulation.strftime("%Y-%m-%d %H:%M"), 
            c.get_statut_display(),
            c.candidat.nom, 
            c.candidat.prenom, 
            c.candidat.email,
            c.candidat.telephone,
            c.candidat.date_naissance.strftime("%Y-%m-%d") if c.candidat.date_naissance else '',
            c.candidat.get_sexe_display(),
            c.candidat.adresse,
            c.candidat.ville,
            c.candidat.pays,
            c.candidat.titre_profil,
            c.get_niveau_etude_display(),
            c.annee_experience,
            'Oui' if c.permis else 'Non',
            request.build_absolute_uri(c.lettre_de_motivation.url) if c.lettre_de_motivation else '',
            request.build_absolute_uri(c.cv.url) if c.cv else '',
            request.build_absolute_uri(c.cin.url) if c.cin else '',
            request.build_absolute_uri(c.diplome.url) if c.diplome else '',
            c.candidat.linkedin_url,
            c.candidat.github_url,
            c.candidat.resume_professionnel
        ])
    
    return response

    # views.py
from django.shortcuts import render, redirect
from .models import Candidat
from .forms import CandidatForm

def modifier_profil(request):
    candidat_id = request.session.get('candidat_id')
    if not candidat_id:
        return redirect('candidat_login')  # à adapter

    candidat = Candidat.objects.get(id=candidat_id)

    if request.method == 'POST':
        form = CandidatForm(request.POST, instance=candidat)
        if form.is_valid():
            form.save()
            return redirect('candidat_dashboard')  # ou autre vue de retour
    else:
        form = CandidatForm(instance=candidat)

    return render(request, 'candidat/modifier_profil.html', {'form': form})
