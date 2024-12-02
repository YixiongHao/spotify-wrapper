"""Unit tests for spotify_data/views (adding and updating users)."""

from unittest.mock import patch, Mock, MagicMock
import json
from datetime import datetime
import pytest
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import SpotifyToken
from spotify_data.views import update_or_add_spotify_user, add_spotify_wrapped, add_duo_wrapped
from spotify_data.models import SpotifyUser, SpotifyWrapped
from spotify_data.views import display_artists, display_genres


def mock_getenv_side_effect(key):
    """
    Create mock groq api key
    Arguments:
        key - the name of the mock key

    Returns:
        the key
    """
    env_vars = {
        'GROQ_API_KEY': key
    }
    return env_vars.get(key)

mock_getenv_side_effect = mock_getenv_side_effect("groq")

@pytest.fixture
def user():
    """Fixture to create a user instance."""
    return User.objects.create_user(username='testuser', password='password')


@pytest.fixture
def mock_spotify_user():
    """
    Fixture to create SpotifyUser instance
    """
    spotify_user = Mock(spec=SpotifyUser)
    spotify_user.display_name = "test_user"
    spotify_user.favorite_artists_short = ["artist1", "artist2"]
    spotify_user.favorite_tracks_short = ["track1", "track2"]
    spotify_user.quirkiest_artists_short = ["quirky_artist1"]
    spotify_user.favorite_genres_short = ["genre1", "genre2"]

    spotify_user.favorite_artists_medium = ["artist3", "artist4"]
    spotify_user.favorite_tracks_medium = ["track3", "track4"]
    spotify_user.quirkiest_artists_medium = ["quirky_artist2"]
    spotify_user.favorite_genres_medium = ["genre3", "genre4"]

    spotify_user.favorite_artists_long = ["artist5", "artist6"]
    spotify_user.favorite_tracks_long = ["track5", "track6"]
    spotify_user.quirkiest_artists_long = ["quirky_artist3"]
    spotify_user.favorite_genres_long = ["genre5", "genre6"]

    spotify_user.past_roasts = []
    return spotify_user

@pytest.fixture
def mock_spotify_user2():
    """
    Fixture to create second SpotifyUser (for duowrapped tests)
    """
    spotify_user2 = Mock(spec=SpotifyUser)
    spotify_user2.display_name = "test_user2"
    spotify_user2.favorite_artists_short = ["artistA", "artistB"]
    spotify_user2.favorite_tracks_short = ["trackA", "trackB"]
    spotify_user2.quirkiest_artists_short = ["quirky_artistA"]
    spotify_user2.favorite_genres_short = ["genreA", "genreB"]

    spotify_user2.favorite_artists_medium = ["artistC", "artistD"]
    spotify_user2.favorite_tracks_medium = ["trackC", "trackD"]
    spotify_user2.quirkiest_artists_medium = ["quirky_artistB"]
    spotify_user2.favorite_genres_medium = ["genreC", "genreD"]

    spotify_user2.favorite_artists_long = ["artistE", "artistF"]
    spotify_user2.favorite_tracks_long = ["trackE", "trackF"]
    spotify_user2.quirkiest_artists_long = ["quirky_artistC"]
    spotify_user2.favorite_genres_long = ["genreE", "genreF"]

    spotify_user2.past_roasts = []
    return spotify_user2

@pytest.fixture
def mock_request(mocker):
    """Fixture to mock the request object."""
    mock = mocker.Mock()
    mock.user = mocker.Mock()  # Mock user object
    return mock


@pytest.fixture
def session_id():
    """Instantiates test session id."""
    return "test_session_id"


@pytest.fixture
def mock_token():
    """Instantiates test access token."""
    return {
        'access_token': 'test_access_token',
        'expires_in': timezone.now() + timezone.timedelta(seconds=3600),  # 1 hour
        'refresh_token': 'test_refresh_token',
        'token_type': 'Bearer'
    }


@pytest.fixture
def mock_user_data():
    """Instantiates test user data."""
    return {
        'id': 'spotify_user_id',
        'display_name': 'Test User',
        'email': 'testuser@example.com',
        'images': [{'url': 'http://example.com/image.jpg'}]
    }

@pytest.mark.django_db
@patch('accounts.views.load_dotenv')
@patch('accounts.views.os.getenv')
def test_missing_access_token(request, user):
    """Test when access token does not exist."""
    request.user = user

    # Patch the is_spotify_authenticated function
    with patch('accounts.views.is_spotify_authenticated', return_value=True), \
            patch('accounts.models.SpotifyToken.objects.get', side_effect=ObjectDoesNotExist):
        response = update_or_add_spotify_user(request)

        assert response.status_code == 500  # Adjusted to match the expected behavior
        assert response.content == b'User add/update failed: missing access token'


# @pytest.mark.django_db
# @patch('accounts.views.load_dotenv')
# @patch('accounts.views.os.getenv')
# def test_successful_user_update(mock_os, mock_load_env, session_id,
#                                 request, mock_token, mock_user_data, user):
#     """Test successful user update when the user already exists."""
#     # Create a mock request object
#     request = Mock()
#     request.session = Mock()
#     request.session.session_key = session_id
#     request.user = user
#
#     # Create the token with a valid datetime for expires_in
#     token_entry = SpotifyToken.objects.create(
#         username=session_id,
#         access_token=mock_token['access_token'],
#         expires_in=timezone.now() + timezone.timedelta(seconds=3600)  # 1 hour from now
#     )
#
#     with patch('accounts.views.is_spotify_authenticated', return_value=True), \
#             patch('accounts.models.SpotifyToken.objects.get', return_value=token_entry), \
#             patch('spotify_data.views.get_spotify_user_data', return_value=mock_user_data), \
#             patch('spotify_data.views.get_user_favorite_tracks',
#                   return_value=['Track1', 'Track2']), \
#             patch('spotify_data.views.get_user_favorite_artists',
#                   return_value=[
#                       {
#                           "id": "artist_id_1",
#                           "name": "Artist1",
#                           "genres": ["Genre1", "Genre2"],
#                           "images": [{"url": "image_url_1"}],
#                           "popularity": 0.6
#                       },
#                       {
#                           "id": "artist_id_2",
#                           "name": "Artist2",
#                           "genres": ["Genre3"],
#                           "images": [{"url": "image_url_2"}],
#                           "popularity": 0.8
#                       }
#                   ]):
#         response = update_or_add_spotify_user(request)
#         assert response.status_code == 200
#         response_data = json.loads(response.content)
#         assert response_data['spotify_user']['created'] is True
#         assert 'spotify_user' in response_data

@pytest.mark.django_db
@patch('accounts.views.os.getenv')
def test_failed_user_data_fetch(request, session_id, mock_token, user):
    """Test when fetching user data from Spotify fails."""
    # Create a mock request object
    request = Mock()
    request.session = Mock()
    request.session.session_key = session_id
    request.user = user

    token_entry = SpotifyToken(username=session_id, access_token=mock_token['access_token'],
                               expires_in=timezone.now() + timezone.timedelta(seconds=3600))
    SpotifyToken.objects.create(username=session_id, **mock_token)

    with patch('accounts.views.is_spotify_authenticated', return_value=True), \
            patch('accounts.models.SpotifyToken.objects.get', return_value=token_entry), \
            patch('spotify_data.views.get_spotify_user_data', return_value=None):
        response = update_or_add_spotify_user(request)
        assert response.status_code == 500
        assert json.loads(response.content) == {'error': 'Could not fetch user data from Spotify'}



@patch('spotify_data.views.SpotifyWrappedSerializer')  # Patch the serializer
@patch('spotify_data.views.SpotifyUser.objects.get')  # Patch SpotifyUser retrieval
@patch('spotify_data.views.SpotifyToken.objects.get')  # Patch SpotifyToken retrieval
@patch('spotify_data.views.create_groq_description')  # Patch description generator
@patch('spotify_data.views.SpotifyWrapped.objects.create')  # Patch object creation
def test_add_spotify_wrapped_short_term(mock_create_wrapped,
                                        mock_create_description, mock_get_token,
                                        mock_get_user, mock_serializer):
    """
    Test SpotifyWrapped creation for short-term data
    """
    # Mock request user
    mock_user = Mock(username="test_user")
    mock_get_user.return_value = Mock(
        display_name="test_user",
        favorite_artists_short=["artist1", "artist2"],
        favorite_tracks_short=["track1", "track2"],
        favorite_genres_short=["genre1", "genre2"],
        quirkiest_artists_short=["quirky_artist1"],
        past_roasts=[]
    )

    # Mock token with access_token as a string
    mock_get_token.return_value = Mock(access_token="mock_access_token")

    # Mock description and recommendations
    mock_create_description.return_value = "Generated description"

    # Define a mock datetime
    mock_datetime_created = datetime(2024, 11, 29, 12, 0, 0, 123456)
    formatted_datetime = mock_datetime_created.strftime("%Y-%m-%d-%H-%M-%S-%f")

    # Mock SpotifyWrapped creation and serializer
    mock_created_wrapped = Mock(
        user="test_user",
        favorite_artists=["artist1", "artist2"],
        favorite_tracks=["track1", "track2"],
        favorite_genres=["genre1", "genre2"],
        quirkiest_artists=["quirky_artist1"],
        llama_description="Generated description",
        llama_songrecs=["placeholder1", "placeholder2", "placeholder3"],
        datetime_created=formatted_datetime,
    )
    mock_create_wrapped.return_value = mock_created_wrapped
    mock_serializer.return_value.data = {
        "user": "test_user",
        "favorite_artists": ["artist1", "artist2"],
        "favorite_tracks": ["track1", "track2"],
        "favorite_genres": ["genre1", "genre2"],
        "quirkiest_artists": ["quirky_artist1"],
        "llama_description": "Generated description",
        "llama_songrecs": ["placeholder1", "placeholder2", "placeholder3"],
        "datetime_created": formatted_datetime
    }

    # Simulate the request
    mock_request = MagicMock()

    mock_request.GET.get.return_value = '0'

    assert mock_request.GET.get('termselection') == '0'

    # Call the function
    response = add_spotify_wrapped(mock_request)

    # Assertions
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200

    # Verify the creation call
    mock_create_wrapped.assert_called_once_with(
        user="test_user",
        term_selection='0',
        favorite_artists=["artist1", "artist2"],
        favorite_tracks=["track1", "track2"],
        favorite_genres=["genre1", "genre2"],
        quirkiest_artists=["quirky_artist1"],
        llama_description="Generated description",
        llama_songrecs=["placeholder1", "placeholder2", "placeholder3"],
    )

    # Ensure serializer output is in the response
    response_data = json.loads(response.content)
    assert 'spotify_wrapped' in response_data
    assert response_data['spotify_wrapped'] == mock_serializer.return_value.data


@patch('spotify_data.views.SpotifyWrappedSerializer')  # Patch the serializer
@patch('spotify_data.views.SpotifyUser.objects.get')  # Patch SpotifyUser retrieval
@patch('spotify_data.views.SpotifyToken.objects.get')  # Patch SpotifyToken retrieval
@patch('spotify_data.views.create_groq_description')  # Patch description generator
@patch('spotify_data.views.SpotifyWrapped.objects.create')  # Patch object creation
def test_add_spotify_wrapped_medium_term(mock_create_wrapped,
                                        mock_create_description, mock_get_token,
                                        mock_get_user, mock_serializer):
    """
    Test SpotifyWrapped creation for short-term data
    """
    # Mock request user
    mock_user = Mock(username="test_user")
    mock_get_user.return_value = Mock(
        display_name="test_user",
        favorite_artists_medium=["artist1", "artist2"],
        favorite_tracks_medium=["track1", "track2"],
        favorite_genres_medium=["genre1", "genre2"],
        quirkiest_artists_medium=["quirky_artist1"],
        past_roasts=[]
    )

    # Mock token with access_token as a string
    mock_get_token.return_value = Mock(access_token="mock_access_token")

    # Mock description and recommendations
    mock_create_description.return_value = "Generated description"

    # Mock SpotifyWrapped creation and serializer
    mock_created_wrapped = Mock(
        user="test_user",
        favorite_artists=["artist1", "artist2"],
        favorite_tracks=["track1", "track2"],
        favorite_genres=["genre1", "genre2"],
        quirkiest_artists=["quirky_artist1"],
        llama_description="Generated description",
        llama_songrecs=["placeholder1", "placeholder2", "placeholder3"],
    )
    mock_create_wrapped.return_value = mock_created_wrapped
    mock_serializer.return_value.data = {
        "user": "test_user",
        "favorite_artists": ["artist1", "artist2"],
        "favorite_tracks": ["track1", "track2"],
        "favorite_genres": ["genre1", "genre2"],
        "quirkiest_artists": ["quirky_artist1"],
        "llama_description": "Generated description",
        "llama_songrecs": ["placeholder1", "placeholder2", "placeholder3"],
    }

    # Simulate the request
    mock_request = MagicMock()

    mock_request.GET.get.return_value = '1'

    assert mock_request.GET.get('termselection') == '1'

    # Call the function
    response = add_spotify_wrapped(mock_request)

    # Assertions
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200

    # Verify the creation call
    mock_create_wrapped.assert_called_once_with(
        user="test_user",
        term_selection='1',
        favorite_artists=["artist1", "artist2"],
        favorite_tracks=["track1", "track2"],
        favorite_genres=["genre1", "genre2"],
        quirkiest_artists=["quirky_artist1"],
        llama_description="Generated description",
        llama_songrecs=["placeholder1", "placeholder2", "placeholder3"],
    )

    # Ensure serializer output is in the response
    response_data = json.loads(response.content)
    assert 'spotify_wrapped' in response_data
    assert response_data['spotify_wrapped'] == mock_serializer.return_value.data




@patch('spotify_data.views.SpotifyWrappedSerializer')  # Patch the serializer
@patch('spotify_data.views.SpotifyUser.objects.get')  # Patch SpotifyUser retrieval
@patch('spotify_data.views.SpotifyToken.objects.get')  # Patch SpotifyToken retrieval
@patch('spotify_data.views.create_groq_description')  # Patch description generator
@patch('spotify_data.views.SpotifyWrapped.objects.create')  # Patch object creation
def test_add_spotify_wrapped_long_term(mock_create_wrapped,
                                        mock_create_description, mock_get_token,
                                        mock_get_user, mock_serializer):
    """
    Test SpotifyWrapped creation for short-term data
    """
    # Mock request user
    mock_user = Mock(username="test_user")
    mock_get_user.return_value = Mock(
        display_name="test_user",
        favorite_artists_long=["artist1", "artist2"],
        favorite_tracks_long=["track1", "track2"],
        favorite_genres_long=["genre1", "genre2"],
        quirkiest_artists_long=["quirky_artist1"],
        past_roasts=[]
    )

    # Mock token with access_token as a string
    mock_get_token.return_value = Mock(access_token="mock_access_token")

    # Mock description and recommendations
    mock_create_description.return_value = "Generated description"

    # Mock SpotifyWrapped creation and serializer
    mock_created_wrapped = Mock(
        user="test_user",
        favorite_artists=["artist1", "artist2"],
        favorite_tracks=["track1", "track2"],
        favorite_genres=["genre1", "genre2"],
        quirkiest_artists=["quirky_artist1"],
        llama_description="Generated description",
        llama_songrecs=["placeholder1", "placeholder2", "placeholder3"],
    )
    mock_create_wrapped.return_value = mock_created_wrapped
    mock_serializer.return_value.data = {
        "user": "test_user",
        "favorite_artists": ["artist1", "artist2"],
        "favorite_tracks": ["track1", "track2"],
        "favorite_genres": ["genre1", "genre2"],
        "quirkiest_artists": ["quirky_artist1"],
        "llama_description": "Generated description",
        "llama_songrecs": ["placeholder1", "placeholder2", "placeholder3"],
    }

    # Simulate the request
    mock_request = MagicMock()

    mock_request.GET.get.return_value = '2'

    assert mock_request.GET.get('termselection') == '2'

    # Call the function
    response = add_spotify_wrapped(mock_request)

    # Assertions
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200

    # Verify the creation call
    mock_create_wrapped.assert_called_once_with(
        user="test_user",
        term_selection='2',
        favorite_artists=["artist1", "artist2"],
        favorite_tracks=["track1", "track2"],
        favorite_genres=["genre1", "genre2"],
        quirkiest_artists=["quirky_artist1"],
        llama_description="Generated description",
        llama_songrecs=["placeholder1", "placeholder2", "placeholder3"],
    )

    # Ensure serializer output is in the response
    response_data = json.loads(response.content)
    assert 'spotify_wrapped' in response_data
    assert response_data['spotify_wrapped'] == mock_serializer.return_value.data


@patch('spotify_data.views.SpotifyUser.objects.get')
@patch('spotify_data.views.SpotifyToken.objects.get')
@patch('spotify_data.views.create_groq_description')
@patch('spotify_data.views.SpotifyWrapped.objects.create')
def test_add_spotify_wrapped_invalid_term(mock_create_wrapped,
                                          mock_create_description, mock_get_token,
                                          mock_get_user, mock_request, mock_spotify_user):
    """
    Test proper exit for bad term selection
    """
    # Set up mock user and token
    mock_request.user = Mock()
    mock_get_user.return_value = mock_spotify_user
    mock_get_token.return_value = Mock()  # Mock token object
    mock_create_description.return_value = "Generated description"
    mock_create_wrapped.return_value = Mock(spec=SpotifyWrapped)

    response = add_spotify_wrapped(mock_request)

    assert isinstance(response, HttpResponse)
    assert response.status_code == 400
    mock_create_wrapped.assert_not_called()
    mock_spotify_user.save.assert_not_called()


#     # Assertions
#     assert isinstance(response, JsonResponse)
#     assert response.status_code == 200

#     # Verify creation call
#     mock_create_duo.assert_called_once_with(
#         user1="test_user",
#         user2="test_user2",
#         favorite_artists=["artist1", "artist2", "artistA", "artistB"],
#         favorite_tracks=["track1", "track2", "trackA", "trackB"],
#         favorite_genres=["genre1", "genre2", "genreA", "genreB"],
#         quirkiest_artists=["quirky_artist1", "quirky_artistA"],
#         llama_description="Generated description",
#         llama_songrecs=["placeholder1", "placeholder2", "placeholder3"],
#     )

#     # Ensure both users' past roasts were updated
#     mock_spotify_user.save.assert_called_once_with(update_fields=['past_roasts'])
#     mock_spotify_user2.save.assert_called_once_with(update_fields=['past_roasts'])

#     # Verify response contains serialized data including formatted datetime_created
#     response_data = json.loads(response.content)
#     assert 'duo_wrapped' in response_data
#     assert response_data['duo_wrapped'] == mock_serializer.return_value.data


@patch('spotify_data.views.SpotifyUser.objects.get')
@patch('spotify_data.views.DuoWrapped.objects.create')
def test_add_duo_wrapped_user_not_found(mock_create, mock_get, mock_request, mock_spotify_user):
    """
    Test proper exit for invalid user display name
    """
    mock_get.side_effect = [mock_spotify_user, SpotifyUser.DoesNotExist]

    response = add_duo_wrapped(mock_request)

    assert isinstance(response, HttpResponse)
    assert response.status_code == 500
    mock_create.assert_not_called()
    mock_spotify_user.save.assert_not_called()

@pytest.mark.django_db
@patch("spotify_data.models.DuoWrapped.objects.filter")
@patch("spotify_data.views.create_groq_comparison")
def test_display_artists_duo(mock_comparison, mock_filter, mock_request):
    """
    Test display_artists with DuoWrapped data.
    """
    mock_request.GET.get.side_effect = lambda key: {"id": "1", "isDuo": "true"}.get(key)
    mock_filter.return_value.values.return_value = [{"favorite_artists": [{"name": "Artist 1", "images": [{"url": "http://example.com/img.jpg"}]}]}]
    mock_comparison.return_value = "Generated description"

    response = display_artists(mock_request)
    assert response.status_code == 200
    assert json.loads(response.content)[0]["name"] == "Artist 1"

from unittest.mock import Mock, patch
import pytest
from django.http import JsonResponse
import json

from unittest.mock import Mock, patch
import pytest
from django.http import JsonResponse
import json

@pytest.mark.django_db
@patch("spotify_data.views.DuoWrappedSerializer")
@patch("spotify_data.models.DuoWrapped.objects.create")
@patch("spotify_data.models.SpotifyUser.objects.get")
@patch("spotify_data.views.create_groq_description")
def test_add_duo_wrapped_success(
    mock_create_description, mock_get_user, mock_create_duo_wrapped, mock_serializer, mock_request
):
    """
    Test successful creation of DuoWrapped data.
    """
    # Mock request parameters
    mock_request.GET.get.side_effect = lambda key: {"user1": "user1", "user2": "user2", "termselection": "0"}.get(key)

    # Mock SpotifyUser objects
    mock_user1 = Mock(
        display_name="user1",
        favorite_artists_short=["artist1"],
        favorite_tracks_short=["track1"],
        favorite_genres_short=["genre1", "genre2"],
        quirkiest_artists_short=["quirky_artist1"],
        past_roasts=[],
    )
    mock_user2 = Mock(
        display_name="user2",
        favorite_artists_short=["artist2"],
        favorite_tracks_short=["track2"],
        favorite_genres_short=["genre2"],
        quirkiest_artists_short=["quirky_artist2"],
        past_roasts=[],
    )
    mock_get_user.side_effect = [mock_user1, mock_user2]

    # Mock create_groq_description
    mock_create_description.return_value = "Generated description"

    # Mock DuoWrapped.objects.create
    mock_wrapped_instance = Mock()
    mock_create_duo_wrapped.return_value = mock_wrapped_instance

    # Mock DuoWrappedSerializer
    mock_serializer.return_value.data = {
        "id": 1,
        "user": "user1",
        "user2": "user2",
        "term_selection": "0",
        "favorite_artists": ["artist1", "artist2"],
        "favorite_tracks": ["track1", "track2"],
        "quirkiest_artists": ["quirky_artist1", "quirky_artist2"],
        "favorite_genres": ["genre1", "genre2"],
        "llama_description": "Generated description",
        "llama_songrecs": "none",
    }

    # Call the function
    response = add_duo_wrapped(mock_request)

    # Assertions
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    data = json.loads(response.content)
    assert "duo_wrapped" in data
    assert data["duo_wrapped"]["favorite_artists"] == ["artist1", "artist2"]
    assert data["duo_wrapped"]["llama_description"] == "Generated description"



@pytest.mark.django_db
@patch("spotify_data.models.SpotifyUser.objects.get")
def test_add_duo_wrapped_user2_not_found(mock_get_user, mock_request):
    """
    Test handling of user2 not found for DuoWrapped.
    """
    mock_request.GET.get.side_effect = lambda key: {"user1": "user1", "user2": "invalid_user", "termselection": "0"}.get(key)
    mock_get_user.side_effect = [Mock(), SpotifyUser.DoesNotExist]

    response = add_duo_wrapped(mock_request)
    assert isinstance(response, HttpResponse)
    assert response.status_code == 500
    assert response.content == b"User display name not found"


@pytest.mark.django_db
@patch("spotify_data.views.create_groq_description")
@patch("spotify_data.models.DuoWrapped.objects.filter")
def test_display_genres_duo_success(mock_duo_filter, mock_groq_description, mock_request):
    """
    Test display_genres with DuoWrapped data.
    """
    # Simulate query parameters in the request
    mock_request.GET.get.side_effect = lambda key: {"id": "1", "isDuo": "true"}.get(key)

    # Mock the database query result
    mock_duo_filter.return_value.values.return_value = [
        {"id": "1", "favorite_genres": ["Genre 1", "Genre 2"]}
    ]

    # Mock the create_groq_description function return value
    mock_groq_description.return_value = "Generated description"

    # Call the view function
    response = display_genres(mock_request)

    # Validate the response
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["genres"] == "Genre 1, Genre 2"
    assert "desc" in data
    assert data["desc"] == "Generated description"


@pytest.mark.django_db
@patch("spotify_data.models.DuoWrapped.objects.get")
def test_display_genres_duo_no_data(mock_get_duo, mock_request):
    """
    Test display_genres with DuoWrapped data when no data is found.
    """
    mock_request.GET.get.side_effect = lambda key: {"id": "1", "isDuo": "true"}.get(key)
    mock_get_duo.side_effect = ObjectDoesNotExist
    response = display_genres(mock_request)
    assert response.status_code == 500
    assert response.content == b"Wrapped grab failed: no data"


@pytest.mark.django_db
@patch("spotify_data.models.SpotifyWrapped.objects.filter")
def test_display_genres_single_no_data(mock_filter, mock_request):
    """
    Test display_genres with SpotifyWrapped data when no data is found.
    """
    mock_request.GET.get.side_effect = lambda key: {"id": "1", "isDuo": "false"}.get(key)
    response = display_genres(mock_request)
    assert response.status_code == 500
    assert response.content == b"Wrapped grab failed: no data"

