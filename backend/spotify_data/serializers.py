"""
This module contains serializers for the spotify_data app.
"""
from rest_framework import serializers
from .models import SpotifyUser


class SpotifyUserSerializer(serializers.ModelSerializer):
    """Serializer for the SpotifyUser model."""

    class Meta:
        model = SpotifyUser
        fields = '__all__'
