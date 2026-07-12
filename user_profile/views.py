from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView

from allauth.account.forms import LoginForm, SignupForm
from allauth.account.views import LogoutView

from hotel.forms import UserForm, UserProfileForm
from user_profile.models import UserProfile


# -------------------------
# Auth views
# -------------------------

def register(request):
    form = SignupForm()
    return render(request, "register.html", {"form": form})


def login(request):
    form = LoginForm()
    return render(request, "login.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class CustomLogoutView(LogoutView):
    template_name = "logout.html"

    def get_next_url(self):
        return reverse_lazy("hotel:home")

    def logout(self):
        response = super().logout()
        messages.success(self.request, "You have been successfully logged out.")
        return response


# -------------------------
# User profile
# -------------------------

@login_required
def editar_perfil(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("user_profile:profile")
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }

    return render(request, "editar_perfil.html", context)


@login_required
def profile(request):
    return render(request, "profile.html")


class ChangeUsername(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["username"]
    template_name = "change_username.html"
    success_url = reverse_lazy("user_profile:profile")

    def get_object(self, queryset=None):
        return self.request.user


# -------------------------
# Static pages
# -------------------------

def contact(request):
    return render(request, "contact.html")


def thanks(request):
    return render(request, "thanks.html")


# -------------------------
# Admin / clients
# -------------------------

@login_required
def clients(request):
    users = User.objects.filter(is_superuser=False, is_staff=False)
    return render(request, "clients.html", {"users": users})

