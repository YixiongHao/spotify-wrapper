"""
This module contains utility functions for interacting with the Spotify API.
It includes functions to retrieve user tokens and fetch top data (artists or tracks).
"""

import requests


def get_user_tokens(session_key):
    """
    Retrieves the Spotify access tokens for a user based on their session key.

    Parameters:
        session_key (str): The session key associated with the user's session.

    Returns:
        dict: A dictionary containing the user's access tokens if found, None otherwise.
    """
    # Placeholder: Replace with actual token retrieval logic from the database or session storage
    return {
        'access_token': 'user_access_token',  # Replace with actual token retrieval logic
        'refresh_token': 'user_refresh_token'
    }


def get_spotify_top_data(access_token, data_type, time_range='short_term'):
    """
    Retrieves the top data (artists or tracks) from Spotify for a user.

    Parameters:
        access_token (str): The user's Spotify access token.
        data_type (str): The type of data to retrieve ('artists' or 'tracks').
        time_range (str): The time range for top data ('short_term', 'medium_term', 'long_term').

    Returns:
        list: A list of dictionaries containing the top artists or tracks.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the API request.
    """
    url = f'https://api.spotify.com/v1/me/top/{data_type}?time_range={time_range}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Added a timeout to the request to avoid indefinite hanging
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    return data['items']
