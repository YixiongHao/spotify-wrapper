"""
Models for Spotify Roasted database.
"""
from django.db import models
from django.contrib.auth.models import User

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
    - display_name: username as seen on Spotify
    - email: user's registered email address
    - profile_image_url: link to user's profile picture

    - favorite_tracks_short: a list of 20 favorite tracks over 4 weeks
    - favorite_tracks_medium: a list of 20 favorite tracks over 6 months
    - favorite_tracks_long: a list of 20 favorite tracks over 12 months
    - favorite_artists_short: a list of 20 favorite artists over 4 weeks
    - favorite_artists_medium: a list of 20 favorite artists over 6 months
    - favorite_artists_long: a list of 20 favorite artists over 12 months
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)

    # Add fields to store summarized data
    favorite_tracks_short = models.JSONField(blank=True, null=True)
    favorite_tracks_medium = models.JSONField(blank=True, null=True)
    favorite_tracks_long = models.JSONField(blank=True, null=True)
    favorite_artists_short = models.JSONField(blank=True, null=True)
    favorite_artists_medium = models.JSONField(blank=True, null=True)
    favorite_artists_long = models.JSONField(blank=True, null=True)
