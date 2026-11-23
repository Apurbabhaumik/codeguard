from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max, Avg, Count
from django.shortcuts import render, redirect, get_object_or_404

from assignments.models import Assignment
from .forms import SubmissionForm
from .models import Submission, SimilarityReport
from .similarity import compare_submissions


@login_required
def submit_code(request, slug):
    """
    Handles a student's code submission (POST, CSRF-protected via the
    {% csrf_token %} tag in the template) and, on success, runs the
    similarity engine against every prior submission for the same
    assignment — this is the core "automated review" behaviour.
    """
    assignment = get_object_or_404(Assignment, slug=slug)

    if not assignment.is_open:
        messages.error(request, 'This assignment is past its deadline.')
        return redirect('assignments:detail', slug=slug)

    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            try:
                submission.save()
            except IntegrityError:
                messages.error(request, 'You have already submitted for this assignment.')
                return redirect('assignments:detail', slug=slug)

            _run_similarity_checks(submission)
            messages.success(request, 'Submission received and analyzed.')
            return redirect('submissions:report', pk=submission.pk)
    else:
        form = SubmissionForm()

    return render(request, 'submissions/submit_code.html', {'form': form, 'assignment': assignment})


def _run_similarity_checks(new_submission):
    """
    Compares the new submission against every other submission already
    on file for the same assignment, stores a SimilarityReport row per
    pair, and caches the highest score on the submission itself for
    fast dashboard sorting (an ORM aggregate, not computed per request).
    """
    others = Submission.objects.filter(
        assignment=new_submission.assignment
    ).exclude(pk=new_submission.pk)

    best_score = 0.0
    for other in others:
        result = compare_submissions(new_submission.code, other.code)

        # Keep a stable (lower id, higher id) pair ordering so the
        # unique constraint never collides regardless of comparison order.
        a, b = sorted([new_submission, other], key=lambda s: s.pk)

        SimilarityReport.objects.update_or_create(
            submission_a=a,
            submission_b=b,
            defaults={
                'assignment': new_submission.assignment,
                'token_similarity': result['token_similarity'],
                'structure_similarity': result['structure_similarity'],
                'combined_score': result['combined_score'],
                'flagged': result['combined_score'] >= new_submission.assignment.similarity_threshold,
            },
        )
        best_score = max(best_score, result['combined_score'])

    new_submission.max_similarity = best_score
    new_submission.save(update_fields=['max_similarity'])


@login_required
def submission_report(request, pk):
    submission = get_object_or_404(Submission, pk=pk)

    is_owner = submission.student_id == request.user.id
    is_instructor = getattr(request.user, 'profile', None) and request.user.profile.is_instructor
    if not (is_owner or is_instructor):
        messages.error(request, "You don't have permission to view that report.")
        return redirect('dashboard')

    reports = SimilarityReport.objects.filter(
        submission_a=submission
    ) | SimilarityReport.objects.filter(submission_b=submission)
    reports = reports.order_by('-combined_score')

    return render(request, 'submissions/report.html', {
        'submission': submission,
        'reports': reports,
    })


@login_required
def instructor_dashboard(request, slug):
    profile = getattr(request.user, 'profile', None)
    if not (profile and profile.is_instructor):
        messages.error(request, 'Instructor access required.')
        return redirect('dashboard')

    assignment = get_object_or_404(Assignment, slug=slug)

    submissions = assignment.submissions.select_related('student').order_by('-max_similarity')

    # ORM aggregation (Unit V) for the analytics strip at the top of the dashboard.
    stats = assignment.submissions.aggregate(
        total=Count('id'),
        avg_similarity=Avg('max_similarity'),
        highest_similarity=Max('max_similarity'),
    )
    flagged_count = assignment.reports.filter(flagged=True).count()

    return render(request, 'submissions/instructor_dashboard.html', {
        'assignment': assignment,
        'submissions': submissions,
        'stats': stats,
        'flagged_count': flagged_count,
    })
