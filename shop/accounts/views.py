from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile
from .forms import RegisterForm, LoginForm, ProfileChangeForm, CustomPasswordChangeForm


def register(request):
  if request.user.is_authenticated:
    return redirect("base:index")

  if request.method == "POST":
    form = RegisterForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      messages.success(request, "Реєстрація пройшла успішно!")
      return redirect("base:index")
    messages.error(request, "Помилка реєстрації. Неправильна інформація!")
  else:
    form = RegisterForm()

  return render(request, "accounts/signupLogin.html", {"form": form, "login": False})


def loginUser(request):
  if request.user.is_authenticated:
    return redirect("base:index")

  if request.method == "POST":
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
      username = form.cleaned_data.get("username")
      password = form.cleaned_data.get("password")
      user = authenticate(username=username, password=password)
      if user is not None:
        login(request, user)
        messages.info(request, "Ви успішно ввійшли в акаунт")
        return redirect("base:index")
      else:
        messages.error(request, "Неправильний логін або пароль")
    else:
      messages.error(request, "Неправильний логін або пароль")
  else:
    form = LoginForm()

  return render(request, "accounts/signupLogin.html", {"form": form, "login": True})


@login_required
def logoutUser(request):
  logout(request)
  messages.info(request, "Ви успішно вийшли із акаунта")
  return redirect("accounts:login")


@login_required
def profile(request):
  profile = Profile.objects.get(user=request.user)
  return render(request, "accounts/userProfile.html", {"profile": profile})


@login_required
def change_profile(request):
  if request.method == "POST":
    form = ProfileChangeForm(request.POST, instance=request.user)
    if form.is_valid():
      form.save()
      messages.success(request, "Дані успішно оновлено!")
      return redirect("accounts:profile")
    else:
      messages.error(request, "Помилка. Неправильні дані!")
  else:
    data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
    }
    form = ProfileChangeForm(data)

  return render(request, "accounts/changeProfile.html", {"form": form})


class UpdatePassword(LoginRequiredMixin, PasswordChangeView):
  login_url = "/login/"
  form_class = CustomPasswordChangeForm
  success_url = "/profile/"
  template_name = "accounts/changeProfile.html"

  def form_valid(self, form):
    response = super().form_valid(form)
    messages.success(self.request, "Пароль змінено успішно")
    return response
