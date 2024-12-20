"""
Views for managing Spotify user data, including updating user profiles,
fetching favorite tracks and artists, and generating dynamic descriptions using Groq API.
"""

import os
from dotenv import load_dotenv  # Third-party imports
from rest_framework import viewsets
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from accounts.models import SpotifyToken  # Local imports
from .utils import (get_spotify_user_data, get_user_favorite_artists,
                    get_user_favorite_tracks,
                    get_top_genres, get_quirkiest_artists,
                    create_groq_description,
                    create_groq_quirky, create_groq_comparison)
from .models import Song, SpotifyUser, SpotifyWrapped, DuoWrapped
from .serializers import (SongSerializer, SpotifyUserSerializer,
                          DuoWrappedSerializer, SpotifyWrappedSerializer)

# pylint: disable=too-many-ancestors
class SongViewSet(viewsets.ModelViewSet):
    """
    For testing, API endpoint that allows songs to be viewed or edited.
    """
    queryset = Song.objects.all()  # pylint: disable=no-member
    serializer_class = SongSerializer

# Added the SpotifyUserViewSet class
class SpotifyUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Spotify users to be viewed or edited.
    """
    queryset = SpotifyUser.objects.all()  # pylint: disable=no-member
    serializer_class = SpotifyUserSerializer



def update_or_add_spotify_user(request):
    """
    Adds or updates the user's profile, favorite tracks, and dynamic description
    generated by the Llama3 API based on their music preferences.
    """

    # Load environment variables for later use
    user = request.user
    # Check for existing SpotifyToken
    try:
        token_entry = SpotifyToken.objects.get(username=user.username) # pylint: disable=no-member
    except ObjectDoesNotExist:
        return HttpResponse("User add/update failed: missing access token", status=500)

    access_token = token_entry.access_token

    # Fetch user data from Spotify API
    user_data = get_spotify_user_data(access_token)

    if user_data:
        # Update or create the SpotifyUser
        tracks_short = get_user_favorite_tracks(access_token, 'short_term')
        tracks_medium = get_user_favorite_tracks(access_token, 'medium_term')
        tracks_long = get_user_favorite_tracks(access_token, 'long_term')
        artists_short = get_user_favorite_artists(access_token, 'short_term')
        artists_medium = get_user_favorite_artists(access_token, 'medium_term')
        artists_long = get_user_favorite_artists(access_token, 'long_term')
        genres_short = get_top_genres(artists_short)
        genres_medium = get_top_genres(artists_medium)
        genres_long = get_top_genres(artists_long)
        quirky_short = get_quirkiest_artists(artists_short)
        quirky_medium = get_quirkiest_artists(artists_medium)
        quirky_long = get_quirkiest_artists(artists_long)
        #llama_description = get_groq_description(groq_api_key, artists_long)
        # this has been added for demonstration purposes
        spotify_user, created = SpotifyUser.objects.update_or_create(  # pylint: disable=no-member
            spotify_id=user_data['id'],
            defaults={
                'user': user,
                'spotify_id': user_data.get('id'),
                'display_name': user.username,
                'email': user_data.get('email'),
                'profile_image_url': user_data.get('images')[0]['url']
                if user_data.get('images') else None,
                'favorite_tracks_short': tracks_short,
                'favorite_tracks_medium': tracks_medium,
                'favorite_tracks_long': tracks_long,
                'favorite_artists_short': artists_short,
                'favorite_artists_medium': artists_medium,
                'favorite_artists_long': artists_long,
                'favorite_genres_short': genres_short,
                'favorite_genres_medium': genres_medium,
                'favorite_genres_long': genres_long,
                'quirkiest_artists_short': quirky_short,
                'quirkiest_artists_medium': quirky_medium,
                'quirkiest_artists_long': quirky_long
            }
        )
        return JsonResponse({'spotify_user': SpotifyUserSerializer(spotify_user).data})


    return JsonResponse({'error': 'Could not fetch user data from Spotify'}, status=500)

def add_spotify_wrapped(request):
    """
    Adds a Spotify Wrapped containing all necessary information to the user's profile.
    Parameters:
        - request: incoming web request.
        - term_selection: short_term, medium_term, or long_term. User-selected.
    """
    load_dotenv()
    groq_api_key = os.getenv('GROQ_API_KEY')
    term_selection = request.GET.get('termselection')
    user = request.user
    spotify_user = SpotifyUser.objects.get(display_name=user.username) # pylint: disable=no-member
    favorite_artists = None
    favorite_tracks = None
    favorite_genres = None
    quirkiest_artists = None
    match term_selection:
        case '0':
            favorite_artists = spotify_user.favorite_artists_short
            favorite_tracks = spotify_user.favorite_tracks_short
            favorite_genres = spotify_user.favorite_genres_short
            quirkiest_artists = spotify_user.quirkiest_artists_short
        case '1':
            favorite_artists = spotify_user.favorite_artists_medium
            favorite_tracks = spotify_user.favorite_tracks_medium
            favorite_genres = spotify_user.favorite_genres_medium
            quirkiest_artists = spotify_user.quirkiest_artists_medium
        case '2':
            favorite_artists = spotify_user.favorite_artists_long
            favorite_tracks = spotify_user.favorite_tracks_long
            favorite_genres = spotify_user.favorite_genres_long
            quirkiest_artists = spotify_user.quirkiest_artists_long
    if favorite_artists is None:
        return HttpResponse("Bad term selection", status=400)
    wrapped = SpotifyWrapped.objects.create(  # pylint: disable=no-member
        user=spotify_user.display_name,
        favorite_artists=favorite_artists,
        favorite_tracks=favorite_tracks,
        favorite_genres=favorite_genres,
        quirkiest_artists=quirkiest_artists,
        llama_description=create_groq_description(groq_api_key, favorite_artists),
        llama_songrecs=["placeholder1", "placeholder2", "placeholder3"],)

    wrapped_data = SpotifyWrappedSerializer(wrapped).data
    spotify_user.past_roasts.append(wrapped_data)
    spotify_user.save(update_fields=['past_roasts'])
    return JsonResponse({'spotify_wrapped': wrapped_data})


def add_duo_wrapped(request):
    """
    Adds a Duo Wrapped containing all necessary information to both users' profiles.
    Parameters:
        - request: incoming web request.
        - user2: display name of invited user.
        - term_selection: short_term, medium_term, or long_term. Selected by user1.
    """
    load_dotenv()
    groq_api_key = os.getenv('GROQ_API_KEY')
    user1 = request.GET.get('user1')
    user2 = request.GET.get('user2')
    term_selection = request.GET.get('termselection')

    spotify_user1 = SpotifyUser.objects.get(display_name=user1)  # pylint: disable=no-member
    try:
        spotify_user2 = SpotifyUser.objects.get(display_name=user2)  # pylint: disable=no-member
    except SpotifyUser.DoesNotExist:  # pylint: disable=no-member
        return HttpResponse("User display name not found", status=500)

    favorite_artists = None
    favorite_tracks = None
    favorite_genres = None
    quirkiest_artists = None

    # Helper function to alternate between two lists
    def alternate_lists(list1, list2, count1, count2):
        combined = []
        for i in range(max(count1, count2)):
            if i < count1:
                combined.append(list1[i])
            if i < count2:
                combined.append(list2[i])
        return combined

    match term_selection:
        case '0':
            favorite_artists = alternate_lists(
                spotify_user1.favorite_artists_short, spotify_user2.favorite_artists_short, 3, 2)
            favorite_tracks = alternate_lists(
                spotify_user1.favorite_tracks_short, spotify_user2.favorite_tracks_short, 3, 2)
            favorite_genres = alternate_lists(
                spotify_user1.favorite_genres_short, spotify_user2.favorite_genres_short, 3, 2)
            quirkiest_artists = alternate_lists(
                spotify_user1.quirkiest_artists_short, spotify_user2.quirkiest_artists_short, 3, 2)
        case '1':
            favorite_artists = alternate_lists(
                spotify_user1.favorite_artists_medium, spotify_user2.favorite_artists_medium, 3, 2)
            favorite_tracks = alternate_lists(
                spotify_user1.favorite_tracks_medium, spotify_user2.favorite_tracks_medium, 3, 2)
            favorite_genres = alternate_lists(
                spotify_user1.favorite_genres_medium, spotify_user2.favorite_genres_medium, 3, 2)
            quirkiest_artists = alternate_lists(
                spotify_user1.quirkiest_artists_medium, spotify_user2.quirkiest_artists_medium, 3, 2)
        case '2':
            favorite_artists = alternate_lists(
                spotify_user1.favorite_artists_long, spotify_user2.favorite_artists_long, 3, 2)
            favorite_tracks = alternate_lists(
                spotify_user1.favorite_tracks_long, spotify_user2.favorite_tracks_long, 3, 2)
            favorite_genres = alternate_lists(
                spotify_user1.favorite_genres_long, spotify_user2.favorite_genres_long, 3, 2)
            quirkiest_artists = alternate_lists(
                spotify_user1.quirkiest_artists_long, spotify_user2.quirkiest_artists_long, 3, 2)

    if favorite_artists is None:
        return HttpResponse("Bad term selection", status=400)

    wrapped = DuoWrapped.objects.create(  # pylint: disable=no-member
        user=spotify_user1.display_name,
        user2=spotify_user2.display_name,
        favorite_artists=favorite_artists,
        favorite_tracks=favorite_tracks,
        quirkiest_artists=quirkiest_artists,
        favorite_genres=favorite_genres,
        llama_description=create_groq_description(groq_api_key, favorite_artists),
        llama_songrecs='none'
    )

    wrapped_data = DuoWrappedSerializer(wrapped).data
    spotify_user1.past_roasts.append(wrapped_data)
    spotify_user1.save(update_fields=['past_roasts'])
    spotify_user2.past_roasts.append(wrapped_data)
    spotify_user2.save(update_fields=['past_roasts'])

    print(wrapped.id)
    return JsonResponse({'duo_wrapped': wrapped_data})

def display_artists(request):
    """Displays artists for the frontend depending on the timeframe"""
    load_dotenv()
    id = request.GET.get('id')
    is_duo = request.GET.get('isDuo')
    if is_duo == 'true':
        try:
            wrapped_data = DuoWrapped.objects.filter(id=id).values()
        except ObjectDoesNotExist:
            return HttpResponse("Wrapped grab failed: no data", status=500)
        wrapped_data = list(wrapped_data)[0]
    else:
        try:
            wrapped_data = SpotifyWrapped.objects.filter(id=id).values()
        except ObjectDoesNotExist:
            return HttpResponse("Wrapped grab failed: no data", status=500)
        wrapped_data = list(wrapped_data)[0]

    # Assume artists are limited to top 5 as per the original code
    artists = wrapped_data['favorite_artists'][:5]

    out = []
    for i, artist in enumerate(artists):
        artist_info = {
            'name': artist['name'],
            'image': artist['images'][0]['url'],
            'desc': create_groq_description(os.getenv('GROQ_API_KEY'), artist['name']),
        }
        if is_duo == 'true':
        # Add comparison with the next artist if it exists
            if i + 1 < len(artists):
                next_artist = artists[i + 1]
                comparison = create_groq_comparison(
                    os.getenv('GROQ_API_KEY'),
                    {'name': artist['name'], 'popularity': artist.get('popularity', 0)},
                    {'name': next_artist['name'], 'popularity': next_artist.get('popularity', 0)}
                )
                artist_info['desc'] = comparison

        out.append(artist_info)

    return JsonResponse(out, safe=False, status=200)

def display_genres(request):
    '''Displays the genres for the frontend depending on the timeframe'''
    load_dotenv()
    id = request.GET.get('id')
    is_duo = request.GET.get('isDuo')

    if is_duo == 'true':
        try:
            wrapped_data = DuoWrapped.objects.get(id=id)
        except ObjectDoesNotExist:
            return HttpResponse("Wrapped grab failed: no data", status=500)
    else:
        try:
            wrapped_data = SpotifyWrapped.objects.filter(id=id).values()
        except ObjectDoesNotExist:
            return HttpResponse("Wrapped grab failed: no data", status=500)
    wrapped_data = list(wrapped_data)[0]
    genres = wrapped_data['favorite_genres'][:5]

    out = {
        'genres': ', '.join(genres),
        'desc': create_groq_description(os.getenv('GROQ_API_KEY'), ', '.join(genres))
    }
    return JsonResponse(out, safe=False, status=200)

def display_songs(request):
    """Displays the songs for the frontend depending on the timeframe."""
    load_dotenv()
    id = request.GET.get('id')
    is_duo = request.GET.get('isDuo')

    # Fetch the appropriate wrapped data (DuoWrapped or SpotifyWrapped)
    try:
        if is_duo == 'true':
            wrapped_data = DuoWrapped.objects.filter(id=id).values()
        else:
            wrapped_data = SpotifyWrapped.objects.filter(id=id).values()
    except ObjectDoesNotExist:
        return HttpResponse("Wrapped grab failed: no data", status=500)

    wrapped_data = list(wrapped_data)[0]

    # Get the top 5 tracks
    tracks = wrapped_data['favorite_tracks'][:5]

    out = []
    for i, track in enumerate(tracks):
        artist_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'image': track['album']['images'][0]['url'],
            'desc': create_groq_description(os.getenv('GROQ_API_KEY'),
                                            track['name'] + ' by ' + track['artists'][0]['name'])
        }

        # Add duo comparison logic
        if is_duo == 'true' and i + 1 < len(tracks):
            next_track = tracks[i + 1]
            comparison = create_groq_comparison(
                os.getenv('GROQ_API_KEY'),
                track['name'] + " by " + track['artists'][0]['name'],
                next_track['name'] + " by " + next_track['artists'][0]['name'],
            )
            artist_info['desc'] = comparison

        out.append(artist_info)

    return JsonResponse(out, safe=False, status=200)

def display_quirky(request):
    '''Displays the songs for the frontend depending on the timeframe'''
    load_dotenv()
    id = request.GET.get('id')

    is_duo = request.GET.get('isDuo')

    if is_duo == 'true':
        try:
            wrapped_data = DuoWrapped.objects.filter(id=id).values()
        except ObjectDoesNotExist:
            return HttpResponse("Wrapped grab failed: no data", status=500)
    else:
        try:
            wrapped_data = SpotifyWrapped.objects.filter(id=id).values()
        except ObjectDoesNotExist:
            return HttpResponse("Wrapped grab failed: no data", status=500)
    wrapped_data = list(wrapped_data)[0]
    tracks = wrapped_data['quirkiest_artists'][:5]
    out = []
    for track in tracks:
        out.append(track['name'])

    desc = create_groq_quirky(os.getenv('GROQ_API_KEY'),
                                            ', '.join(out))
    return JsonResponse(desc, safe=False, status=200)

def display_summary(request):
    '''Displays a summary of a users music taste'''
    load_dotenv()
    id = request.GET.get('id')

    is_duo = request.GET.get('isDuo')

    if is_duo == 'true':
        try:
            wrapped_data = DuoWrapped.objects.filter(id=id).values()
        except ObjectDoesNotExist:
            return HttpResponse("Wrapped grab failed: no data", status=500)
    else:
        try:
            wrapped_data = SpotifyWrapped.objects.filter(id=id).values()
        except ObjectDoesNotExist:
            return HttpResponse("Wrapped grab failed: no data", status=500)
    wrapped_data = list(wrapped_data)[0]
    artists = wrapped_data['favorite_artists'][:5]
    genres = wrapped_data['favorite_genres'][:5]
    tracks = wrapped_data['favorite_tracks'][:5]
    quirky = wrapped_data['quirkiest_artists'][0] if wrapped_data['quirkiest_artists'] else ""

    artist_list = []
    for artist in artists:
        artist_list.append(artist['name'])

    tracks_list = []
    for track in tracks:
        tracks_list.append(track['name'])

    summary = {
        'artists': artist_list,
        'tracks': tracks_list,
        'quirky': quirky['name'] if quirky else "",
        'genres': genres
    }

    return JsonResponse(summary, safe=False, status=200)

def display_history(request):
    '''Display history of wraps for a user'''
    user = request.user

    try:
        user_data = SpotifyUser.objects.get(display_name=user.username)
    except ObjectDoesNotExist:
        return HttpResponse("User grab failed: no data", status=500)

    ids = []
    for roast in user_data.past_roasts:
        if roast.get('user') == user.username:
            di = {
                'id': roast['id'],
                'isDuo': 'user2' in roast
            }
            ids.append(di)

    # Return an empty list if no roasts found for the user
    if not ids:
        return JsonResponse([], safe=False, status=200)

    return JsonResponse(ids, safe=False, status=200)


def check_username_exists(request):
    """
    Check if a username exists in the database.
    """
    username = request.GET.get('username')  # Get the username from the request

    users = SpotifyUser.objects.all()  # Retrieve all SpotifyUser objects
    for user in users:
        print(user.display_name)

    if not username:
        return JsonResponse({'error': 'No username provided'}, status=400)

    try:
        # Query the database for the username
        SpotifyUser.objects.filter(display_name=username)
        return JsonResponse({'exists': True}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({'exists': False}, status=200)
