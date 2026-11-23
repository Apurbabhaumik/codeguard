from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from assignments.models import Assignment
from submissions.models import Submission


@login_required
def dashboard(request):
    """
    Landing page after login. Renders a different view depending on
    role, both served by the same base template (Unit III: template
    inheritance) via an {% if %} switch inside dashboard.html.
    """
    profile = getattr(request.user, 'profile', None)
    is_instructor = bool(profile and profile.is_instructor)

    if is_instructor:
        assignments = Assignment.objects.filter(created_by=request.user)
        context = {'is_instructor': True, 'assignments': assignments}
    else:
        assignments = Assignment.objects.all()
        my_submissions = Submission.objects.filter(student=request.user).select_related('assignment')
        submitted_ids = set(my_submissions.values_list('assignment_id', flat=True))
        context = {
            'is_instructor': False,
            'assignments': assignments,
            'my_submissions': my_submissions,
            'submitted_ids': submitted_ids,
        }

    return render(request, 'dashboard.html', context)


def landing(request):
    """
    Public marketing page at "/". Signed-in users skip straight to
    their role-specific dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')
