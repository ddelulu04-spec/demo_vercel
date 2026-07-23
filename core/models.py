# Create your models here.
from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Candidate(models.Model):
    STATUS_CHOICES = [
        ('Shortlist', 'Shortlist'),
        ('Reject', 'Reject'),
        ('Consider', 'Consider'),
        ('Pending', 'Pending'),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    cv_file = models.FileField(upload_to='cvs/')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    match_score = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    ai_summary = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-match_score']