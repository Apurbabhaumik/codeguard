from django.contrib import admin

from .models import Submission, SimilarityReport


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'max_similarity', 'submitted_at')
    list_filter = ('assignment',)
    search_fields = ('student__username', 'assignment__title')


@admin.register(SimilarityReport)
class SimilarityReportAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'submission_a', 'submission_b', 'combined_score', 'flagged')
    list_filter = ('flagged', 'assignment')
    ordering = ('-combined_score',)
