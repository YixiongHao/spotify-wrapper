from django.shortcuts import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import get
from accounts.models import SpotifyUser
from accounts.utils import get_user_tokens, is_spotify_authenticated


# Helper function to make Spotify API requests
def make_spotify_api_request(url, access_token):
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

    This view collects the user's favorite tracks and artists over different time ranges
    and stores them in the SpotifyUser model.

    Methods:
        get(self, request):
            Handles GET requests to retrieve and store Spotify user data.
    """

    def get(self, request):
        """
        Handles GET request to retrieve and store Spotify user data.

        Fetches the access tokens for the authenticated user and retrieves data from Spotify API
        for top tracks and artists over short, medium, and long time ranges. The data is
        then stored in the `SpotifyUser` model.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response (rest_framework.response.Response):
                A JSON response indicating success or failure.
        """
        # Check if the user is authenticated with Spotify
        user = request.user
        if not is_spotify_authenticated(request.session.session_key):
            return Response({'error': 'User is not authenticated with Spotify'}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve the user's Spotify tokens
        tokens = get_user_tokens(request.session.session_key)
        if not tokens:
            return Response({'error': 'Could not retrieve Spotify tokens'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token = tokens.access_token

        # Spotify API URLs for top tracks and artists over different time periods
        top_tracks_url_short = 'https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=20'
        top_tracks_url_medium = 'https://api.spotify.com/v1/me/top/tracks?time_range=medium_term&limit=20'
        top_tracks_url_long = 'https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=20'

        top_artists_url_short = 'https://api.spotify.com/v1/me/top/artists?time_range=short_term&limit=20'
        top_artists_url_medium = 'https://api.spotify.com/v1/me/top/artists?time_range=medium_term&limit=20'
        top_artists_url_long = 'https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=20'

        # Fetch top tracks and artists from Spotify API
        favorite_tracks_short = make_spotify_api_request(top_tracks_url_short, access_token)
        favorite_tracks_medium = make_spotify_api_request(top_tracks_url_medium, access_token)
        favorite_tracks_long = make_spotify_api_request(top_tracks_url_long, access_token)

        favorite_artists_short = make_spotify_api_request(top_artists_url_short, access_token)
        favorite_artists_medium = make_spotify_api_request(top_artists_url_medium, access_token)
        favorite_artists_long = make_spotify_api_request(top_artists_url_long, access_token)

        # Update or create the SpotifyUser record for the current user
        spotify_user, created = SpotifyUser.objects.get_or_create(user=user)
        spotify_user.favorite_tracks_short = favorite_tracks_short.get('items') if favorite_tracks_short else []
        spotify_user.favorite_tracks_medium = favorite_tracks_medium.get('items') if favorite_tracks_medium else []
        spotify_user.favorite_tracks_long = favorite_tracks_long.get('items') if favorite_tracks_long else []

        spotify_user.favorite_artists_short = favorite_artists_short.get('items') if favorite_artists_short else []
        spotify_user.favorite_artists_medium = favorite_artists_medium.get('items') if favorite_artists_medium else []
        spotify_user.favorite_artists_long = favorite_artists_long.get('items') if favorite_artists_long else []

        # Save the updated SpotifyUser instance
        spotify_user.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
