from django.shortcuts import render
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



def register(request):
    form = SignupForm()
    return render(request, 'register.html', {'form': form})

def clients(request):
    users = User.objects.filter(is_superuser=False, is_staff=False)
    user_image = ["https://bootdey.com/img/Content/avatar/avatar4.png","https://bootdey.com/img/Content/avatar/avatar5.png",
                  "https://bootdey.com/img/Content/avatar/avatar6.png","https://bootdey.com/img/Content/avatar/avatar7.png",
                  "https://bootdey.com/img/Content/avatar/avatar6.png","https://bootdey.com/img/Content/avatar/avatar1.png",
                  "https://bootdey.com/img/Content/avatar/avatar3.png"]

    return render(request, 'clients.html', {'users': users})

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
            return render(self.request, 'home.html')
        else:
            return render(self.request, 'home.html')



class ChangeUsername(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ['username']
    template_name = 'change_username.html'
    success_message = 'username updated successfully'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('account_login')



