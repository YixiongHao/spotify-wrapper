"""
This module contains views to retrieve and store Spotify user data.

It interacts with the Spotify API to collect a user's favorite tracks and artists
over short, medium, and long time ranges and stores them in the SpotifyUser model.
"""

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import get
from ..accounts.models import SpotifyUser
from ..accounts.utils import get_user_tokens, is_spotify_authenticated


# Helper function to make Spotify API requests
def make_spotify_api_request(url, access_token):
    """
    Makes an authorized request to the Spotify API.

    Parameters:
    - url: API endpoint to request data from.
    - access_token: The user's Spotify access token for authentication.

    Returns:
    - JSON response from the Spotify API or None if the request fails.
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        return None
    return response.json()


class SpotifyDataView(APIView):
    """
    Class-based view to retrieve and store Spotify data for a specific user.

    It fetches the user's top tracks and artists over short, medium, and long time ranges,
    then stores this data in the SpotifyUser model.
    """

    def get(self, request):
        """
        Handles GET request to retrieve and store Spotify user data.

        It retrieves the user's access tokens and then requests the Spotify API
        for top tracks and artists across different time ranges, updating the
        SpotifyUser model accordingly.

        Parameters:
        - request: HTTP request object.

        Returns:
        - Response indicating success or failure.
        """
        # Check if the user is authenticated with Spotify
        user = request.user
        if not is_spotify_authenticated(request.session.session_key):
            return Response({'error': 'User is not authenticated with Spotify'},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve the user's Spotify tokens
        tokens = get_user_tokens(request.session.session_key)
        if not tokens:
            return Response({'error': 'Could not retrieve Spotify tokens'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token = tokens.access_token

        # Spotify API URLs for top tracks and artists over different time periods
        api_urls = {
            'favorite_tracks_short': (
                'https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=20'
            ),
            'favorite_tracks_medium': (
                'https://api.spotify.com/v1/me/top/tracks?time_range=medium_term&limit=20'
            ),
            'favorite_tracks_long': (
                'https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=20'
            ),
            'favorite_artists_short': (
                'https://api.spotify.com/v1/me/top/artists?time_range=short_term&limit=20'
            ),
            'favorite_artists_medium': (
                'https://api.spotify.com/v1/me/top/artists?time_range=medium_term&limit=20'
            ),
            'favorite_artists_long': (
                'https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=20'
            )
        }

        # Fetch top tracks and artists from Spotify API
        spotify_data = {key: make_spotify_api_request(url, access_token)
                        for key, url in api_urls.items()}

        # Update or create the SpotifyUser record for the current user
        spotify_user, _ = SpotifyUser.objects.get_or_create(user=user)
        spotify_user.favorite_tracks_short = spotify_data['favorite_tracks_short'].get('items', [])
        spotify_user.favorite_tracks_medium = spotify_data['favorite_tracks_medium'].get('items', [])
        spotify_user.favorite_tracks_long = spotify_data['favorite_tracks_long'].get('items', [])
        spotify_user.favorite_artists_short = spotify_data['favorite_artists_short'].get('items', [])
        spotify_user.favorite_artists_medium = spotify_data['favorite_artists_medium'].get('items', [])
        spotify_user.favorite_artists_long = spotify_data['favorite_artists_long'].get('items', [])

        # Save the updated SpotifyUser instance
        spotify_user.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
