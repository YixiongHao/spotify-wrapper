"""
This module contains views for interacting with Spotify API data.
It includes retrieving and storing user's top artists and tracks.
"""

from django.shortcuts import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
import requests

from .models import SpotifyUser
from .utils import get_user_tokens, get_spotify_top_data


class TopArtistsView(APIView):
    """
    Class-based view to retrieve and store a user's top artists from Spotify.

    This view interacts with the Spotify API to fetch the user's top artists based on
    their listening habits and stores them in the SpotifyUser model.
    """

    def get(self, request, time_range='short_term'):
        """
        Handles GET request to fetch and store the user's top artists.

        Retrieves the user's top artists from Spotify for the specified time range
        (short_term, medium_term, long_term) and stores the result in the SpotifyUser model.

        Parameters:
            request (HttpRequest): The HTTP request object.
            time_range (str): The time range for top data (short_term, medium_term, long_term).

        Returns:
            Response (rest_framework.response.Response):
                A JSON response containing the user's top artists or an error message.
        """
        tokens = get_user_tokens(request.session.session_key)

        if not tokens:
            return Response({'error': 'User is not authenticated with Spotify.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            top_artists = get_spotify_top_data(tokens['access_token'], 'artists', time_range)
            spotify_user = SpotifyUser.objects.get(user=request.user)

            if time_range == 'short_term':
                spotify_user.favorite_artists_short = top_artists
            elif time_range == 'medium_term':
                spotify_user.favorite_artists_medium = top_artists
            else:  # long_term
                spotify_user.favorite_artists_long = top_artists

            spotify_user.save()

            return Response({'top_artists': top_artists}, status=status.HTTP_200_OK)
        except SpotifyUser.DoesNotExist:
            return Response({'error': 'Spotify user not found.'}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopTracksView(APIView):
    """
    Class-based view to retrieve and store a user's top tracks from Spotify.

    This view interacts with the Spotify API to fetch the user's top tracks based on
    their listening habits and stores them in the SpotifyUser model.
    """

    def get(self, request, time_range='short_term'):
        """
        Handles GET request to fetch and store the user's top tracks.

        Retrieves the user's top tracks from Spotify for the specified time range
        (short_term, medium_term, long_term) and stores the result in the SpotifyUser model.

        Parameters:
            request (HttpRequest): The HTTP request object.
            time_range (str): The time range for top data (short_term, medium_term, long_term).

        Returns:
            Response (rest_framework.response.Response):
                A JSON response containing the user's top tracks or an error message.
        """
        tokens = get_user_tokens(request.session.session_key)

        if not tokens:
            return Response({'error': 'User is not authenticated with Spotify.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            top_tracks = get_spotify_top_data(tokens['access_token'], 'tracks', time_range)
            spotify_user = SpotifyUser.objects.get(user=request.user)

            if time_range == 'short_term':
                spotify_user.favorite_tracks_short = top_tracks
            elif time_range == 'medium_term':
                spotify_user.favorite_tracks_medium = top_tracks
            else:  # long_term
                spotify_user.favorite_tracks_long = top_tracks

            spotify_user.save()

            return Response({'top_tracks': top_tracks}, status=status.HTTP_200_OK)
        except SpotifyUser.DoesNotExist:
            return Response({'error': 'Spotify user not found.'}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
