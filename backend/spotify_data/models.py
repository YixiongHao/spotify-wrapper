"""
Models for Spotify Roasted database.
"""
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from spotify_data.utils import datetime_to_str

class Song(models.Model):
    """
    Toy model, testing out rest framework
    """
    title = models.CharField(max_length=100)
    runTime = models.IntegerField()

class SpotifyUser(models.Model):
    """
    Model for each Spotify user that registers on our website.
    Never updated after the user registers.

    Parameters:
        - user: links Spotify id to Django User model
        - spotify_id: unique user identifier from Spotify
        - display_name: username as seen on roast account
        - email: user's registered email address
        - profile_image_url: link to user's profile picture

        - favorite_tracks_short: a list of 5 favorite tracks over 4 weeks
        - favorite_tracks_medium: a list of 5 favorite tracks over 6 months
        - favorite_tracks_long: a list of 5 favorite tracks over 12 months
        - favorite_artists_short: a list of 5 favorite artists over 4 weeks
        - favorite_artists_medium: a list of 5 favorite artists over 6 months
        - favorite_artists_long: a list of 5 favorite artists over 12 months
        - favorite_genres_short: a list of 5 favorite genres pulled from favorite_artists_short
        - favorite_genres_medium: a list of 5 favorite genres pulled from favorite_artists_medium
        - favorite_genres_long: a list of 5 favorite genres pulled from favorite_artists_long
        - quirkiest_artists_short: 5 quirkiest artists pulled from favorite_artists_short
        - quirkiest_artists_medium: 5 quirkiest artists pulled from favorite_artists_medium
        - quirkiest_artists_long: 5 quirkiest artists pulled from favorite_artists_long
        - llama_description: gives a description of how the user acts/thinks/dresses using an LLM
        - llama_songrecs: a string containing song recommendation as pulled from the LLM
        - past_roasts: a collection of past Spotify Roasts by this user
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)

    # Add fields to store summarized data
    favorite_tracks_short = models.JSONField(default=list, blank=True, null=True)
    favorite_tracks_medium = models.JSONField(default=list, blank=True, null=True)
    favorite_tracks_long = models.JSONField(default=list, blank=True, null=True)
    favorite_artists_short = models.JSONField(default=list, blank=True, null=True)
    favorite_artists_medium = models.JSONField(default=list, blank=True, null=True)
    favorite_artists_long = models.JSONField(default=list, blank=True, null=True)
    favorite_genres_short = models.JSONField(default=list, blank=True, null=True)
    favorite_genres_medium = models.JSONField(default=list, blank=True, null=True)
    favorite_genres_long = models.JSONField(default=list, blank=True, null=True)
    quirkiest_artists_short = models.JSONField(default=list, blank=True, null=True)
    quirkiest_artists_medium = models.JSONField(default=list, blank=True, null=True)
    quirkiest_artists_long = models.JSONField(default=list, blank=True, null=True)
    past_roasts = models.JSONField(default=list, blank=True, null=True)

class WrapBase(models.Model):
    """
    Abstract base model for shared fields between SpotifyWrapped and DuoWrapped.
    """
    id = models.AutoField(primary_key=True)  # Shared primary key
    user = models.CharField(max_length=100)
    term_selection = models.CharField(max_length=20)
    favorite_artists = models.JSONField(default=list, blank=True, null=True)
    favorite_tracks = models.JSONField(default=list, blank=True, null=True)
    favorite_genres = models.JSONField(default=list, blank=True, null=True)
    quirkiest_artists = models.JSONField(default=list, blank=True, null=True)
    llama_description = models.TextField(blank=True, null=True)
    llama_songrecs = models.TextField(blank=True, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        '''Meta'''
        abstract = True


class SpotifyWrapped(WrapBase):
    """
    Model for individual Spotify Wrapped.
    """



class DuoWrapped(WrapBase):
    """
    Model for Duo Wrapped.
    """
    user2 = models.CharField(max_length=100)  # Additional field for DuoWrapped
