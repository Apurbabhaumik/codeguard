from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView

from .forms import AssignmentForm
from .models import Assignment


class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        profile = getattr(self.request.user, 'profile', None)
        return bool(profile and profile.is_instructor)


class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'assignments/assignment_list.html'
    context_object_name = 'assignments'


class AssignmentCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    success_url = reverse_lazy('assignments:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


@login_required
def assignment_detail(request, slug):
    """
    Demonstrates Unit II: URL params (slug), handling GET for the detail
    page, and keeping error handling explicit via get_object_or_404
    (which raises Http404 -> Django's built-in error view).
    """
    assignment = get_object_or_404(Assignment, slug=slug)
    return render(request, 'assignments/assignment_detail.html', {'assignment': assignment})
