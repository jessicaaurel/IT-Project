import json
from tictactoe.tictactoe_game import play_game_async
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
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

def human_vs_human(request):
    return render(request, 'humanhuman.html')

async def human_vs_ai_game(player1, player2):
    experiment_name = None  # You can set this if you have specific experiments
    cycle_number = 0  # Adjust as needed



    # TODO: This is a temporary fix for the prompt. Assume we always use minimal prompt.
    if (player2 == "gpt4"):
        player2 = "minimal_gpt4_player"
    else:
        player2 = player2 + "_minimal_player"



    log = await play_game_async(player1, player2, experiment_name, cycle_number)
    return log


def about_view(request):
    return render(request, 'about.html')

@csrf_exempt
def human_vs_ai_view(request, ai_model):
    if request.method == "GET":
        return render(request, 'humanai.html', {'ai_model': ai_model})

    if request.method == "POST":

        player1 = 'human_player'
        player2 = ai_model  # This will be 'gemini', 'claude', or 'llama'

        # Requests and reads the outcome of the game
        data = json.loads(request.body)
        gameOutcome = data.get('outcome')
        
        # Use asyncio to run the game asynchronously
        '''
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        log = loop.run_until_complete(human_vs_ai_game(player1, player2))
        '''

        game_result = GameResult.objects.create(
            player_one=request.user,
            ai_model2=ai_model,
            outcome=gameOutcome
        )
        print(f"Saved game result: {game_result}")
        
        # Return the game log as a JSON response
        # return JsonResponse(log, safe=False)

        # TODO: Temporary fix
        return JsonResponse({'message': 'Success'}, status=200)
    
import asyncio
from django.shortcuts import render
from django.http import JsonResponse

# AI vs AI game simulation
async def ai_vs_ai_game(ai1, ai2):
    experiment_name = None  # You can customize this if needed
    cycle_number = 0  # This could represent the round or cycle number
    log = await play_game_async(ai1, ai2, experiment_name, cycle_number)
    return log

# View for AI vs AI
@csrf_exempt
def ai_vs_ai_view(request, ai1_model, ai2_model):
    if request.method == "GET":
        return render(request, 'aivsai.html', {'ai1_model': ai1_model, 'ai2_model': ai2_model})

    if request.method == "POST":
        # Simulate AI vs AI game
        ai1 = ai1_model  # First AI model (e.g., 'gemini')
        ai2 = ai2_model  # Second AI model (e.g., 'claude')

        # Requests and reads the outcome of the game
        data = json.loads(request.body)
        gameOutcome = data.get('outcome')
        
        # Run the game asynchronously
        # TODO: Temporary fix
        '''
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        log = loop.run_until_complete(ai_vs_ai_game(ai1, ai2))
        '''
        game_result = GameResult.objects.create(
            ai_model1=ai1,
            ai_model2=ai2,
            outcome=gameOutcome 
        )
        print(f"Saved game result: {game_result}")

        # Return the game log as a JSON response
        return JsonResponse({'message': 'Success'}, status=200)

@csrf_exempt
def store_game_result(request):
    if request.method == 'POST':
        player_one = User.objects.get(username='human_player')  # Replace with actual player lookup logic
        player_two = User.objects.get(username='AIPlayer')
        outcome = request.POST.get('outcome')

        # Store the result in the database
        GameResult.objects.create(
            player_one=player_one,
            player_two=player_two,
            outcome=outcome
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})