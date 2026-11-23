from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.views import View

from .forms import SignUpForm


class SignUpView(View):
    template_name = 'accounts/signup.html'

    def get(self, request):
        return render(request, self.template_name, {'form': SignUpForm()})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # starts a session for the new user
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


class CodeGuardLoginView(LoginView):
    template_name = 'accounts/login.html'


class CodeGuardLogoutView(LogoutView):
    next_page = 'accounts:login'
