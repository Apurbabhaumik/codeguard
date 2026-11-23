from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Assignment(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('javascript', 'JavaScript'),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    deadline = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    similarity_threshold = models.PositiveSmallIntegerField(
        default=70,
        help_text='Similarity %% at or above this is auto-flagged for review.',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_open(self):
        return timezone.now() < self.deadline

    def submission_count(self):
        return self.submissions.count()
