from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_chore, name='create_chore'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('all-chores/', views.all_chores, name='all_chores'),
    path('chore/<int:chore_id>/', views.chore_details, name='chore_details'),
    path('chore/<int:chore_id>/update-status/', views.update_chore_status, name='update_chore_status'),
    path('update-chore-status-home/<int:chore_id>/', views.update_chore_status_home, name='update_chore_status_home'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
]