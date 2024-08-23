from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Chore(models.Model):
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_chores')
    assigned_to = models.ManyToManyField(User, related_name='assigned_chores')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    points = models.IntegerField(default=1)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username