"""Tests methods from spotify_data/utils."""

import unittest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime
import pytest
from groq import GroqError
from ..utils import (get_spotify_user_data, get_user_favorite_artists, get_user_favorite_tracks,
                     get_top_genres, get_quirkiest_artists, interlock, str_to_datetime,
                     get_spotify_recommendations, create_groq_description)




@pytest.mark.parametrize("status_code, expected_result", [
    (200, {'id': '123', 'display_name': 'Test User', 'email': 'test@example.com'}),
    (404, None),
    (401, None),
])
def test_get_spotify_user_data(status_code, expected_result):
    """Tests that a user's profile can be retrieved."""
    access_token = 'valid_token'
    with patch('requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = status_code
        mock_response.json.return_value = {'id': '123',
       'display_name': 'Test User', 'email': 'test@example.com'} if status_code == 200 else {}

        result = get_spotify_user_data(access_token)
        assert result == expected_result


@pytest.mark.parametrize("status_code, expected_result", [
    (200, [{'name': 'Artist 1'}, {'name': 'Artist 2'}]),
    (404, None),
])
def test_get_user_favorite_artists(status_code, expected_result):
    """Tests that a user's 20 favorites artists can be retrieved"""
    access_token = 'valid_token'
    timelimit = 'short_term'
    with patch('requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = status_code
        mock_response.json.return_value ={'items':
            [{'name': 'Artist 1'}, {'name': 'Artist 2'}]} if status_code == 200 else {}

        result = get_user_favorite_artists(access_token, timelimit)
        assert result == expected_result

@pytest.mark.parametrize("status_code, expected_result", [
    (200, [{'name': 'Track 1'}, {'name': 'Track 2'}]),
    (404, None),
])
def test_get_user_favorite_tracks(status_code, expected_result):
    """Tests that a user's 20 favorite tracks can be retrieved."""
    access_token = 'valid_token'
    timelimit = 'short_term'
    with patch('requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = status_code
        mock_response.json.return_value = {
            'items': [{'name': 'Track 1'}, {'name': 'Track 2'}]} if status_code == 200 else {}

        result = get_user_favorite_tracks(access_token, timelimit)
        assert result == expected_result

class NonAPIFunctions(unittest.TestCase):
    """
    Functions that do not rely on a JSON response from the API.
    """
    def test_get_top_genres(self):
        """
        Tests that artists are properly filtered by top genre
        """
        # Mock data for favorite artists
        favorite_artists = [
            {'name': 'Artist A', 'genres': ['rock', 'pop']},
            {'name': 'Artist B', 'genres': ['pop', 'dance']},
            {'name': 'Artist C', 'genres': ['rock', 'indie']},
            {'name': 'Artist D', 'genres': ['jazz']},
            {'name': 'Artist E', 'genres': ['pop', 'jazz']},
        ]

        # Expected output: top 3 genres
        expected_output = ['pop', 'rock', 'jazz']

        # Call the function
        result = get_top_genres(favorite_artists)

        # Assert that the result matches the expected output
        self.assertEqual(result, expected_output)

    def test_get_quirkiest_artists(self):
        """
        Tests that artists are properly filtered by lowest popularity
        """
        # Mock data for favorite artists with popularity scores
        favorite_artists = [
            {'id': '1', 'name': 'Artist A', 'popularity': 50},
            {'id': '2', 'name': 'Artist B', 'popularity': 20},
            {'id': '3', 'name': 'Artist C', 'popularity': 30},
            {'id': '4', 'name': 'Artist D', 'popularity': 10},
            {'id': '5', 'name': 'Artist E', 'popularity': 60},
            {'id': '6', 'name': 'Artist F', 'popularity': 5},
        ]

        # Expected output: the 5 quirkiest artists (lowest popularity scores)
        expected_output = [
            {'id': '6', 'name': 'Artist F', 'popularity': 5},
            {'id': '4', 'name': 'Artist D', 'popularity': 10},
            {'id': '2', 'name': 'Artist B', 'popularity': 20},
            {'id': '3', 'name': 'Artist C', 'popularity': 30},
            {'id': '1', 'name': 'Artist A', 'popularity': 50},
        ]

        # Call the function
        result = get_quirkiest_artists(favorite_artists)

        # Assert that the result matches the expected output
        self.assertEqual(result, expected_output)


@patch('spotify_data.utils.requests.get')
def test_get_spotify_recommendations(mock_get):
    """Test fetching song recommendations using Spotify API."""
    mock_user_token = "mock_access_token"
    seed_artists = ["artist_id_1"]
    mock_response_data = {'tracks':
        [{
            "id": "track_id_1",
            "name": "Song 1",
            "artists": [{"name": "Artist 1"}],
            "album": {"name": "Album 1"},
            "preview_url": "http://example.com/preview",
            "external_urls": {"spotify": "http://example.com/song"}
        }]}

    mock_response = Mock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    recommendations = get_spotify_recommendations(
        user_token=mock_user_token,
        seed_artists=seed_artists
    )

    assert len(recommendations) == 1
    assert recommendations[0]["name"] == "Song 1"
    assert recommendations[0]["artist"] == "Artist 1"
    assert recommendations[0]["album"] == "Album 1"
    assert recommendations[0]["preview_url"] == "http://example.com/preview"
    assert recommendations[0]["external_url"] == "http://example.com/song"



def test_create_groq_description_returns_response():
    """Test that a response is successfully returned from the Groq API."""
    mock_groq_api_key = "mock_api_key"
    favorite_artists = ["Artist1", "Artist2"]

    # Mock response content
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Sample description."

    # Ensure the patch path matches exactly where Groq is imported in your code
    with patch("spotify_data.utils.Groq") as MockGroq:
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.return_value = mock_response

        # Call the function
        llama_description = create_groq_description(mock_groq_api_key, favorite_artists)

        # Verify that we got a response
        assert llama_description is not None, "Expected a response but got None."

        # Verify that the API was called once
     #mock_client.chat.completions.create.assert_called_once()


def test_create_groq_description_no_api_key():
    """Test that GroqError is raised when no API key is provided."""
    favorite_artists = ["Artist1", "Artist2"]
    with pytest.raises(GroqError, match="GROQ_API_KEY environment variable is not set."):
        create_groq_description("", favorite_artists)


def test_create_groq_description_key_error_handling():
    """Test that the function handles KeyError in the response gracefully."""
    mock_groq_api_key = "mock_api_key"
    favorite_artists = ["Artist1", "Artist2"]

    with patch("spotify_data.utils.Groq") as MockGroq:
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.side_effect = KeyError("choices")

        llama_description = create_groq_description(mock_groq_api_key, favorite_artists)

        assert llama_description is not None, "Expected an error message but got None."


def test_create_groq_description_general_exception_handling():
    """Test that the function handles a general API exception gracefully."""
    mock_groq_api_key = "mock_api_key"
    favorite_artists = ["Artist1", "Artist2"]

    with patch("spotify_data.utils.Groq") as MockGroq:
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.side_effect = Exception("API error")

        llama_description = create_groq_description(mock_groq_api_key, favorite_artists)

        assert llama_description is not None, "Expected an error message but got None."


@pytest.mark.parametrize("favorite_artists", [
    (["Artist1"]),
    (["Artist1", "Artist2", "Artist3"]),
])
def test_create_groq_description_varied_artist_list(favorite_artists):
    """Test with different artist lists to ensure function can retrieve a response."""
    mock_groq_api_key = "mock_api_key"
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Sample description."

    with patch("spotify_data.utils.Groq") as MockGroq:
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.return_value = mock_response

        llama_description = create_groq_description(mock_groq_api_key, favorite_artists)

        assert llama_description is not None, "Expected a response but got None."

def test_str_to_datetime():
    teststr = '2024-01-02-03-04-05-000006'
    assert str_to_datetime(teststr) == datetime(2024, 1, 2, 3, 4, 5, 6)


def test_interlock():
    arr1 = [1, 3, 5]
    arr2 = [2, 4]
    assert interlock(arr1, arr2) == [1, 2, 3, 4, 5]
    arr3 = [1, 3]
    assert interlock(arr3, arr2) == [1, 2, 3, 4]
