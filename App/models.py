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
    updated_at = models.DateTimeField(auto_now=True)  # Add this line
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    points = models.IntegerField(default=1)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def mark_as_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        for user in self.assigned_to.all():
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.increment_chores_completed()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    chores_completed = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def increment_chores_completed(self):
        self.chores_completed += 1
        self.save()