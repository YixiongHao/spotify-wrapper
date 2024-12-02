"""
This file is used to define the URL patterns for the Spotify Data API endpoint
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SongViewSet, update_or_add_spotify_user, add_spotify_wrapped, add_duo_wrapped
from .views import (display_artists, display_genres, display_songs, display_quirky,
                    display_summary, display_history, check_username_exists, delete)

router = DefaultRouter()
router.register(r'songs', SongViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('updateuser', update_or_add_spotify_user,
         name='update_or_add_spotify_user'),
    path('addwrapped/', add_spotify_wrapped, name='add_spotify_wrapped'),
    path('addduo/', add_duo_wrapped, name='add_duo_wrapped'),
    path('displayartists', display_artists, name='display_artists'),
    path('displaygenres', display_genres, name='display_genres'),
    path('displaytracks', display_songs, name='display_songs'),
    path('displayquirky', display_quirky, name='display_quirky'),
    path('displaysummary', display_summary, name='display_summary'),
    path('displayhistory', display_history, name='display_history'),
    path('checkusername', check_username_exists, name='check_username_exists'),
    path('delete', delete, name='delete'),
]
