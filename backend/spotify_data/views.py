"""
Views for managing Spotify user data, including updating user profiles,
fetching favorite tracks and artists, and generating dynamic descriptions using Groq API.
"""

import os  # Standard library import

from dotenv import load_dotenv  # Third-party imports
from rest_framework import viewsets
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from groq import Groq, GroqError

from accounts.models import SpotifyToken  # Local imports
from accounts.utils import is_spotify_authenticated
from .utils import get_spotify_user_data, get_user_favorite_artists, get_user_favorite_tracks
from .models import Song, SpotifyUser
from .serializers import SongSerializer


# Load environment variables
load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

if not groq_api_key:
    raise GroqError("GROQ_API_KEY environment variable is not set.")

client = Groq(api_key=groq_api_key)


# pylint: disable=too-many-ancestors
class SongViewSet(viewsets.ModelViewSet):
    """
    For testing, API endpoint that allows songs to be viewed or edited.
    """
    queryset = Song.objects.all()  # pylint: disable=no-member
    serializer_class = SongSerializer

def update_or_add_spotify_user(request, session_id):
    """
    Adds or updates the user's profile, favorite tracks, and dynamic description
    generated by the Llama3 API based on their music preferences.
    """
    if not is_spotify_authenticated(session_id):
        return JsonResponse({'error': 'User not authenticated'}, status=403)

    user = request.user

    # Check for existing SpotifyToken
    try:
        token_entry = SpotifyToken.objects.get(user=session_id)
    except ObjectDoesNotExist:
        return HttpResponse("User add/update failed: missing access token", status=500)

    access_token = token_entry.access_token

    # Fetch user data from Spotify API
    user_data = get_spotify_user_data(access_token)

    if user_data:
        # Get user's favorite artists and tracks
        favorite_tracks_long = get_user_favorite_tracks(access_token, 'long_term')
        favorite_artists_long = get_user_favorite_artists(access_token, 'long_term')

        # Create a dynamic description using Groq Llama3 API
        description_prompt = (
            f"Describe how someone who listens to artists like {', '.join(favorite_artists_long)} "
            "tends to act, think, and dress."
        )

        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a music analyst who"
                                   " describes user"
                                   " behavior based on their music tastes.",
                    },
                    {
                        "role": "user",
                        "content": description_prompt
                    }
                ],
                model="llama3-8b-8192",
            )

            llama_description = response.choices[0].message.content
        except KeyError as e:
            llama_description = f"Key error: {str(e)}"
        except Exception as e:
            llama_description = f"Description unavailable due to API error: {str(e)}"  # pylint: disable=broad-exception-caught

        # Update or create the SpotifyUser
        spotify_user, created = SpotifyUser.objects.update_or_create(  # pylint: disable=no-member
            spotify_id=user_data['id'],
            defaults={
                'user': user,
                'spotify_id': user_data.get('id'),
                'display_name': user_data.get('display_name'),
                'email': user_data.get('email'),
                'profile_image_url': user_data.get('images')[0]['url']
                if user_data.get('images') else None,
                'favorite_tracks_short': get_user_favorite_tracks(access_token, 'short_term'),
                'favorite_tracks_medium': get_user_favorite_tracks(access_token, 'medium_term'),
                'favorite_tracks_long': favorite_tracks_long,
                'favorite_artists_short': get_user_favorite_artists(access_token, 'short_term'),
                'favorite_artists_medium': get_user_favorite_artists(access_token, 'medium_term'),
                'favorite_artists_long': favorite_artists_long,
                'llama_description': llama_description,  # Save the generated description
            }
        )

        return JsonResponse({'spotify_user': {'id': spotify_user.spotify_id,
                                              'created': created,
                                              'description': llama_description}})

    return JsonResponse({'error': 'Could not fetch user data from Spotify'}, status=500)
