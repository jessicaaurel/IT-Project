from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import GameResult

def summary_view(request):
    results = GameResult.objects.all().order_by('-game_date')
    return render(request, 'summary.html', {'results': results})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def home_view(request):
    if request.user.is_authenticated:
        return render(request, "home.html")
    else:
        return redirect('login')  # Redirect to login if not authenticated


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')  # Redirect to login page after successful registration
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def game_view(request):
    return render (request, 'game.html')

def leaderboard_view(request):
    # Updated dummy AI performance data with draws
    ai_performance = [
        {'name': 'AI Alpha', 'wins': 25, 'losses': 5, 'draws': 3},
        {'name': 'AI Beta', 'wins': 20, 'losses': 10, 'draws': 2},
        {'name': 'AI Gamma', 'wins': 15, 'losses': 15, 'draws': 5},
        {'name': 'AI Delta', 'wins': 10, 'losses': 20, 'draws': 1},
        {'name': 'AI Epsilon', 'wins': 5, 'losses': 25, 'draws': 0},
    ]

    # Sort AI based on wins (or any other criteria later)
    ai_performance_sorted = sorted(ai_performance, key=lambda x: x['wins'], reverse=True)

    return render(request, 'leaderboard.html', {'ai_performance': ai_performance_sorted})


def results_summary(request):
    return render(request, 'results_summary.html')

def results_statistics(request):
    return render(request, 'results_statistics.html')

def about(request):
    return render(request, 'about.html')

def logout_view(request):
    # Handle logout logic here
    return redirect('login')

def summary_view(request):
    results = GameResult.objects.all().order_by('-game_date')  # Get all game results, ordered by most recent
    return render(request, 'summary.html', {'results': results})



