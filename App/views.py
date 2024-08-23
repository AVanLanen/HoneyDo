from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import logout, login
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.template.loader import render_to_string  # Add this import
from .models import Chore, UserProfile
from .forms import ChoreForm, UserRegistrationForm

@login_required
def home(request):
    assigned_chores = Chore.objects.filter(assigned_to=request.user)
    created_chores = Chore.objects.filter(created_by=request.user)
    return render(request, 'home.html', {
        'assigned_chores': assigned_chores,
        'created_chores': created_chores
    })

@login_required
def create_chore(request):
    if request.method == 'POST':
        form = ChoreForm(request.POST)
        if form.is_valid():
            chore = form.save(commit=False)
            chore.created_by = request.user
            chore.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('home')
    else:
        form = ChoreForm()
    
    return render(request, 'chore_form.html', {
        'form': form,
        'title': 'Create Chore',
        'submit_text': 'Create Chore',
        'loading_text': 'Creating'
    })

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    completed_chores = Chore.objects.filter(assigned_to=request.user, status='completed')
    return render(request, 'profile.html', {'profile': user_profile, 'completed_chores': completed_chores})

@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def all_chores(request):
    chores = Chore.objects.all().select_related('created_by').prefetch_related('assigned_to')
    users = User.objects.all()
    return render(request, 'all_chores.html', {'chores': chores, 'users': users})

@login_required
def chore_details(request, chore_id):
    chore = get_object_or_404(Chore, id=chore_id)
    
    if request.method == 'POST':
        form = ChoreForm(request.POST, instance=chore)
        if form.is_valid():
            form.save()
            return redirect('chore_details', chore_id=chore.id)
    else:
        form = ChoreForm(instance=chore)
    
    return render(request, 'chore_form.html', {
        'form': form,
        'chore': chore,
        'title': 'Chore Details',
        'submit_text': 'Update Chore',
        'loading_text': 'Updating'
    })

@login_required
@require_http_methods(["POST"])
def update_chore_status(request, chore_id):
    chore = get_object_or_404(Chore, id=chore_id)
    new_status = request.POST.get('status')
    if new_status in dict(Chore.STATUS_CHOICES):
        chore.status = new_status
        chore.save()
    return redirect('chore_details', chore_id=chore.id)

@login_required
def update_chore_status_home(request, chore_id):
    chore = get_object_or_404(Chore, id=chore_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Chore.STATUS_CHOICES):
            chore.status = new_status
            chore.save()
    
    # Render both assigned and created chores
    assigned_chores = Chore.objects.filter(assigned_to=request.user)
    created_chores = Chore.objects.filter(created_by=request.user)
    
    html = render_to_string('partials/chore_list.html', {
        'assigned_chores': assigned_chores,
        'created_chores': created_chores
    }, request=request)
    
    return HttpResponse(html)