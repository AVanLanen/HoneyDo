from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout, login
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from .models import Chore, UserProfile
from .forms import ChoreForm, UserRegistrationForm
import json  # Add this import

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
    time_frame = request.GET.get('time_frame', 'month')
    
    if time_frame == 'week':
        days_ago = 7
        trunc_func = TruncDate('completed_at')
    elif time_frame == 'month':
        days_ago = 30
        trunc_func = TruncDate('completed_at')
    elif time_frame == '3months':
        days_ago = 90
        trunc_func = TruncWeek('completed_at')
    elif time_frame == 'year':
        days_ago = 365
        trunc_func = TruncMonth('completed_at')
    else:
        days_ago = 30
        trunc_func = TruncDate('completed_at')

    start_date = timezone.now() - timezone.timedelta(days=days_ago)
    
    completed_chores = Chore.objects.filter(
        assigned_to=request.user,
        status='completed',
        completed_at__gte=start_date
    ).order_by('-completed_at')

    # Calculate total completed chores for the selected time frame
    total_completed_chores = completed_chores.count()
    
    # Calculate completion_data
    completion_data = completed_chores.annotate(
        date=trunc_func
    ).values('date').annotate(count=Count('id')).order_by('date')

    filled_completion_data = []
    current_date = start_date
    end_date = timezone.now()

    while current_date <= end_date:
        date_key = current_date.strftime("%Y-%m-%d")
        count = next((item['count'] for item in completion_data if item['date'].strftime("%Y-%m-%d") == date_key), 0)
        filled_completion_data.append({'date': date_key, 'count': count})
        
        if time_frame == 'year':
            current_date += timezone.timedelta(days=32)
            current_date = current_date.replace(day=1)
        elif time_frame == '3months':
            current_date += timezone.timedelta(weeks=1)
        else:
            current_date += timezone.timedelta(days=1)

    # Calculate completion rate
    total_chores = Chore.objects.filter(assigned_to=request.user, created_at__gte=start_date).count()
    completion_rate = round((total_completed_chores / total_chores) * 100, 1) if total_chores > 0 else 0

    context = {
        'profile': user_profile,
        'completed_chores': completed_chores[:5],  # Show only the 5 most recent
        'completion_data': json.dumps(filled_completion_data),
        'completion_rate': completion_rate,
        'time_frame': time_frame,
        'total_completed_chores': total_completed_chores
    }

    if request.htmx:
        return render(request, 'partials/chore_chart.html', context)
    
    return render(request, 'profile.html', context)

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
        if new_status == 'completed':
            chore.mark_as_completed()
        else:
            chore.status = new_status
            chore.save()
    return redirect('chore_details', chore_id=chore.id)

@login_required
def update_chore_status_home(request, chore_id):
    chore = get_object_or_404(Chore, id=chore_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Chore.STATUS_CHOICES):
            if new_status == 'completed':
                chore.mark_as_completed()
            else:
                chore.status = new_status
                chore.save()
    
    # Fetch all chores for the current user
    assigned_chores = Chore.objects.filter(assigned_to=request.user)
    created_chores = Chore.objects.filter(created_by=request.user)
    
    context = {
        'assigned_chores': assigned_chores,
        'created_chores': created_chores
    }
    
    return render(request, 'partials/chore_list.html', context)