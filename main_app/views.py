from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Favorite, Comment
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .forms import CommentForm
import requests

headers = {
    "X-RapidAPI-Key": "a249ee6bfamshfb62e9b1c9d89d2p17b949jsn9d35882504fe",
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}
def league_info(id): 
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
    querystring = {"id": id}
    league = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response'][0]['league']
    return league

def get_league(id, season):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    querystring = {"league": id, "season": season}
    teams = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response']
    return teams


def get_games(team, next):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"team": team, "next": next}
    games = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response']
    return games

def get_last(team, num): 
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"team": team, "last": num, "status": "FT"}
    game = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response'][0]
    return game
    

def fix_timestamp(game):
    game['fixture']['timestamp'] = datetime.fromtimestamp(
        game['fixture']['timestamp'])
    return game


def get_team(id):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    querystring = {"id": id}
    team = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response'][0]
    return team


def get_squad(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/players/squads"
    querystring = {"team": team_id}
    squad = requests.request("GET", url, headers=headers,
                             params=querystring).json()['response'][0]
    return (squad)


def find_live(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"live": "all", "team": team_id}
    live_game = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response']
    return (live_game)


def get_game_info(game_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"id": game_id}
    game = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response'][0]
    return (game)


def get_game_stats(game_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
    querystring = {"fixture": game_id}
    live_stats = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response']
    return live_stats


def get_standings(team_id, season):
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
    querystring = {"season": season, "team": team_id, "type": "league"}
    standings_id = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response'][0]['league']['id']
    url = "https://api-football-v1.p.rapidapi.com/v3/standings"
    querystring = {"season": season, "league": standings_id}
    standings = requests.request(
        "GET", url, headers=headers, params=querystring).json()['response'][0]['league']
    return standings
#  what I want on the home page: 
#  tables for all 5 leagues(to go on team pages)
#  each favorite team's last match
#  each favorite teams next match
#  any live games in the top 5 leagues 
def home(request):
    favorite_info = []
    recent_matches = []
    next_matches = []
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user)
        favorite_ids = []
        for favorite in favorites:
            favorite_ids.append(favorite.team_id)
        for id in favorite_ids: 
            team = get_team(id)
            favorite_info.append(team)
        for id in favorite_ids: 
            recent_match = get_last(id, 1)
            recent_matches.append(recent_match)
        for id in favorite_ids:
            next_match = get_games(id, 1)
            next_matches.append(next_match)
    return render(request, 'home.html', {'favorites': favorite_info,'recents' : recent_matches, 'next' : next_matches})


@login_required
def team_detail(request, team_id):
    team = get_team(team_id)
    upcoming_games = get_games(team_id, 3)
    last_game = get_last(team_id, 1)
    fix_timestamp(last_game)
    for game in upcoming_games:
        fix_timestamp(game)
    squad = get_squad(team_id)
    live_game = find_live(team_id)
    standings = get_standings(team_id, 2022)
    favorite = Favorite.objects.filter(user=request.user, team_id=team_id)
    return render(request, 'team.html', {'team': team, 'upcoming': upcoming_games, 'squad': squad, 'live': live_game, 'last' : last_game, "favorite" : favorite, "standings" : standings})


@login_required
def game_detail(request, game_id):
    game = get_game_info(game_id)
    fix_timestamp(game)
    comment_form = CommentForm()
    live_stats = get_game_stats(game_id)
    comments = Comment.objects.filter(game_id=game_id)
    return render(request, 'game.html', {'game': game, 'stats': live_stats, 'comment_form': comment_form, 'comments': comments})


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


@login_required
def favorite_team(request, team_id):
    new_favorite = Favorite(team_id=team_id, user=request.user)
    new_favorite.save()
    return redirect('team_detail', team_id=team_id)


@login_required
def remove_team(request, team_id):
    team = Favorite.objects.filter(team_id=team_id, user=request.user)
    team.delete()
    return redirect('/')

@login_required
def add_comment(request, game_id):
    form = CommentForm(request.POST)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.game_id = game_id
        new_comment.user = request.user
        new_comment.save()
    return redirect('game_detail', game_id=game_id)


@login_required 
def remove_comment(request, comment_id): 
  comment = Comment.objects.filter(id=comment_id)
  game_id = comment[0].game_id
  comment.delete()
  return redirect('game_detail', game_id=game_id)
    
## manage teams must include: a users favorite teams
@login_required
def manage(request): 
    if request.user.is_authenticated:
        teams = Favorite.objects.filter(user=request.user)
        favorites = []
        for team in teams: 
            team_data = get_team(team.team_id)
            favorites.append(team_data)
    return render(request, 'manage.html', {"favorites" : favorites})

@login_required
def add(request): 
    ids = [39, 140, 135, 78, 61]
    leagues = []
    for id in ids: 
        info = league_info(id)
        leagues.append(info)
    return render(request, 'leagues.html', {'leagues' : leagues})

def add_team(request, league_id): 
    teams = get_league(league_id, 2022)
    favorites = Favorite.objects.filter(user=request.user)
    ids = []
    for favorite in favorites: 
        id = favorite.team_id
        ids.append(id)
    for team in teams: 
        if team['team']['id'] in ids: 
            teams.remove(team)
    return render(request, 'add_teams.html', {"teams" : teams})
