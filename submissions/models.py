from django.contrib.auth.models import User
from django.db import models

from assignments.models import Assignment


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    max_similarity = models.FloatField(default=0.0)  # cached best match, for fast sorting

    class Meta:
        ordering = ['-submitted_at']
        constraints = [
            models.UniqueConstraint(
                fields=['assignment', 'student'],
                name='one_submission_per_student_per_assignment',
            )
        ]

    def __str__(self):
        return f'{self.student.username} -> {self.assignment.title}'


class SimilarityReport(models.Model):
    """
    One row per compared PAIR of submissions for the same assignment.
    submission_a is always the earlier (lower id) of the two, so a pair
    is never stored twice in reversed order.
    """

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='reports')
    submission_a = models.ForeignKey(Submission, related_name='reports_as_a', on_delete=models.CASCADE)
    submission_b = models.ForeignKey(Submission, related_name='reports_as_b', on_delete=models.CASCADE)
    token_similarity = models.FloatField(help_text='Jaccard similarity on normalized tokens (0-100)')
    structure_similarity = models.FloatField(
        null=True, blank=True,
        help_text='AST-shape similarity for Python submissions (0-100); null for other languages',
    )
    combined_score = models.FloatField(help_text='Score used for flagging/sorting (0-100)')
    flagged = models.BooleanField(default=False)
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-combined_score']
        constraints = [
            models.UniqueConstraint(
                fields=['submission_a', 'submission_b'],
                name='one_report_per_pair',
            )
        ]

    def __str__(self):
        return f'{self.submission_a_id} vs {self.submission_b_id}: {self.combined_score:.1f}%'
