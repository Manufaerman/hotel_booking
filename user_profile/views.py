from django.shortcuts import render, get_object_or_404, redirect
from allauth.account.forms import LoginForm, SignupForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from allauth.account.views import LogoutView, LoginView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from hotel.forms import UserForm, UserProfileForm

from user_profile.models import UserProfile


def register(request):
    form = SignupForm()
    return render(request, 'register.html', {'form': form})

def clients(request):
    users = User.objects.filter(is_superuser=False, is_staff=False)

    return render(request, 'clients.html', {'users': users})

@login_required
def editar_perfil(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST or None, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('perfil')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }

    return render(request, 'editar_perfil.html', context)

def profile(request):
    return render(request, 'profile.html')

def contact(request):
    return render(request, 'contact.html')

def thanks(request):
    return render(request, 'thanks.html')


def login(request):
    form = LoginForm
    return render(request, 'login.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class CustomLogoutView(LogoutView):
    template_name = 'logout.html'

    def logout(self):
        response = super().logout()
        messages.success(self.request, 'You have been successfully logged out.')
        return response

    def get_next_url(self):
        # Check user type and redirect accordingly
        if self.request.user.is_staff:
            return render(self.request, '-home.html')
        else:
            return render(self.request, '-home.html')



class ChangeUsername(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ['username']
    template_name = 'change_username.html'
    success_message = 'username updated successfully'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('account_login')



