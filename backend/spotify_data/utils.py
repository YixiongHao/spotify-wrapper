"""
Utils used in spotify_data/views.
"""

from collections import Counter
from datetime import datetime
from groq import Groq,  GroqError
import requests

def get_spotify_user_data(access_token):
    """
    Retrieves current user data including spotify id, email, profile image, and username.

    Parameters:
        - access_token: the access token associated with the current session

    Returns:
        JSON response containing user data
    """

    # Fetch the user's data from Spotify API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get('https://api.spotify.com/v1/me', headers=headers, timeout=5)
    return response.json() if response.status_code == 200 else None

def get_user_favorite_tracks(access_token, timelimit):
    """
    Returns a list of 20 user favorite tracks over one of three time periods:
    - short-term: 4 weeks
    - medium-term: 6 months
    - long-term: 1 year

    Parameters:
        - access_token: the access token associated with the current session
        - timelimit: the desired term

    Returns:
        JSON response containing user favorite tracks
    """

    # Fetch the user's data from Spotify API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'time_range': timelimit,
        'limit': 20
    }
    response = requests.get('https://api.spotify.com/v1/me/top/tracks',
                            headers=headers, params=params, timeout=5)
    return response.json()['items'] if response.status_code == 200 else None

def get_user_favorite_artists(access_token, timelimit):
    """
    Returns a list of 20 user favorite artists over one of three time periods:
    - short-term: 4 weeks
    - medium-term: 6 months
    - long-term: 1 year

    Parameters:
        - access_token: the access token associated with the current session
        - timelimit: the desired term

    Returns:
        JSON response containing user favorite artists
    """

    # Fetch the user's data from Spotify API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'time_range': timelimit,
        'limit': 20
    }
    response = requests.get('https://api.spotify.com/v1/me/top/artists',
                            headers=headers, params=params, timeout=5)
    return response.json()['items'] if response.status_code == 200 else None


def get_top_genres(favorite_artists):
    """
    Extracts genres from a list of favorite artists and returns the top 3 genres.

    Parameters:
        favorite_artists: List of favorite artists from Spotify API containing their genre info.

    Returns:
        List of the top 3 genres.
    """
    genres = []

    # Extract genres from each artist
    for artist in favorite_artists:
        genres.extend(artist['genres'])

    # Count the occurrences of each genre
    genre_counts = Counter(genres)

    # Get the top 3 genres
    top_genres = genre_counts.most_common(3)

    # Return only the genre names (not the counts)
    return [genre for genre, count in top_genres]

def get_quirkiest_artists(favorite_artists):
    """
    Returns the 5 quirkiest artists based on their popularity scores.

    Parameters:
        - favorite_artists: a list of favorite artists
                (dictionaries with 'id', 'name', and 'popularity')

    Returns:
        A list of the 5 quirkiest artists based on popularity scores.
    """
    # Sort the artists by popularity (lower scores are quirkier)
    sorted_artists = sorted(favorite_artists, key=lambda x: x['popularity'])

    # Return the top 5 quirkiest artists
    return sorted_artists[:5]

def create_groq_description(groq_api_key, favorite_artists):
    """
    Create a description of user tastes/ lifestyle based on favorite artists

    Args:
        - favorite_artists: List of favorite artists
        (dictionaries with 'id', 'name', and 'popularity')

    Returns:
        - llama_description: the description construced by the LLM

    """
    if not groq_api_key:
        raise GroqError("GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=groq_api_key)
    description_prompt = (
        f"Describe how someone who listens to artists like {favorite_artists} "
        "tends to act, think, and dress."
    )

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a music analyst who roasts and insults the user "
                               "(use 2nd perspective) behavior based on their music tastes"
                               " in less than 100 words."
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
    return llama_description


SPOTIFY_RECOMMENDATIONS_URL = "https://api.spotify.com/v1/recommendations"

def get_spotify_recommendations(user_token, seed_artists=None,
                                seed_tracks=None, seed_genres=None):
    """
    Fetches a list of recommended songs from Spotify based on provided seeds and target attributes.

    Args:
        user_token (str): The Spotify access token for the user.
        seed_artists (list of str): List of Spotify artist IDs to base recommendations on.
        seed_tracks (list of str): List of Spotify track IDs to base recommendations on.
        seed_genres (list of str): List of genres to base recommendations on.


    Returns:
        list: A list of recommended songs, where each song
        is represented as a dictionary with details.
    """
    headers = {
        "Authorization": f"Bearer {user_token}"
    }

    params = {
        "limit": 5,
    }
    if seed_artists:
        params["seed_artists"] = ",".join(seed_artists)
    if seed_tracks:
        params["seed_tracks"] = ",".join(seed_tracks)
    if seed_genres:
        params["seed_genres"] = ",".join(seed_genres)


    try:
        response = requests.get(SPOTIFY_RECOMMENDATIONS_URL,
                                headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()['tracks']

        recommended_songs = [
            {
                "id": track["id"],
                "name": track["name"],
                "artist": ", ".join([artist["name"] for artist in track["artists"]]),
                "album": track["album"]["name"],
                "preview_url": track["preview_url"],
                "external_url": track["external_urls"]["spotify"]
            }
            for track in data
        ]
        return recommended_songs

    except requests.exceptions.RequestException as e:
        print(f"Error fetching recommendations: {e}")
        return []

def create_groq_quirky(groq_api_key, favorite_artists):
    """
    Create a description of user tastes/ lifestyle based on favorite artists

    Args:
        - favorite_artists: List of favorite artists
        (dictionaries with 'id', 'name', and 'popularity')

    Returns:
        - llama_description: the description construced by the LLM

    """
    if not groq_api_key:
        raise GroqError("GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=groq_api_key)
    description_prompt = (
        f"Describe how someone who only listens to artists like {favorite_artists} "
        "just to be quirky and stand out from the crowd tends to act, think, and dress."
    )

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a music analyst who roasts and insults the user "
                               "(use 2nd perspective) behavior based on their music tastes "
                               "in less than 100 words."
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
    return llama_description

def datetime_to_str(dt):
    """
    Convert datetime object to string.
    """
    return dt.strftime("%Y-%m-%d-%H-%M-%S-%f")

def str_to_datetime(dtstr):
    """
    Convert string to datetime object.
    """
    strlist = dtstr.split("-")
    y = int(strlist[0])
    m = int(strlist[1])
    d = int(strlist[2])
    H = int(strlist[3])
    M = int(strlist[4])
    S = int(strlist[5])
    f = int(strlist[6])
    return datetime(y, m, d, H, M, S, f)

def create_groq_comparison(groq_api_key, artist_1, artist_2):
    """
    Create a humorous and roasty comparison between two favorite artists.

    Args:
        - groq_api_key: API key for Groq
        - artist_1: Dictionary containing the first artist's name and additional info
        - artist_2: Dictionary containing the second artist's name and additional info

    Returns:
        - llama_description: A funny roasty description of the comparison between the two artists
    """
    if not groq_api_key:
        raise GroqError("GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=groq_api_key)
    description_prompt = (
        f"Compare {artist_1} and {artist_2} in a funny and way that roasts both. "
        "Highlight their differences in style, fanbase, and "
        "anything else that makes them opposites."
    )

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a music critic who roasts and humorously "
                               "compares two artists "
                               "(use 2nd perspective) in less than 100 words. "
                               "Be witty and sarcastic."
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
        llama_description = f"Comparison unavailable due to API error: {str(e)}"  # pylint: disable=broad-exception-caught
    return llama_description
