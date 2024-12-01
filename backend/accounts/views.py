"""
This module contains views for handling Spotify authentication and authorization,
as well as user account management functions for login, logout, and registration.

It includes class-based and function-based views to handle the Spotify OAuth flow, 
check user authentication status, manage CSRF tokens, and interact with the Spotify API.

Classes:
    - AuthURL: Returns the Spotify authorization URL to initiate OAuth.
    - IsAuthenticated: Checks if a user is authenticated with Spotify.

Functions:
    - spotify_callback: Handles the Spotify redirect after user authorization and stores tokens.
    - get_csrf_token: Ensures that a CSRF token is set for frontend requests.
    - sign_in: Authenticates and logs in the user.
    - sign_out: Logs out the user and returns a success message.
    - sign_up: Registers a new user, validates username and password criteria, and logs them in.
"""
import os
from django.http import JsonResponse
from django.shortcuts import HttpResponse, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from requests import Request, post
from .utils import update_or_create_user_tokens, is_spotify_authenticated, generate_state, delete_user_data

from .forms import LoginForm, RegisterForm

# Create your views here.

class AuthURL(APIView):
    """
    Class-based view to handle Spotify authentication.

    This view returns a URL that directs the user to Spotify's authorization page.
    Once there, the user can grant permission to the app. This permission is required
    before we can interact with the user's Spotify data.

    Methods:
        get(self, request): 
            Handles GET requests and constructs the Spotify authorization URL 
            with necessary parameters such as scope, response_type, and redirect URI.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handles GET request to create the Spotify authorization URL.

        Loads environment variables to fetch Spotify client credentials and scopes.
        Constructs a URL using the Spotify authorization endpoint and returns it
        in the response.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response (rest_framework.response.Response): 
                A JSON response containing the Spotify authorization URL.
        """
        load_dotenv()

        client_id = os.getenv('CLIENT_ID')
        scope = os.getenv('SCOPE')
        redirect_uri = os.getenv('REDIRECT_URI')

        if not client_id or not scope or not redirect_uri:
            return Response({'error': 'Missing environment variables'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        state = generate_state()
        request.session['spotify_auth_state'] = state

        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scope,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'state': state,
            'show_dialog': 'true'
        }).prepare().url

        return redirect(url)

@login_required
def spotify_callback(request, format=None):
    """
    View to handle the callback from Spotify after user authorization.

    This view processes the authorization code received from Spotify and exchanges
    it for access and refresh tokens, which are stored in the database. This allows 
    future interactions with Spotify on behalf of the user.

    Parameters:
        request (HttpRequest): The HTTP request object containing the Spotify callback data.
    
    Returns:
        HttpResponse: Redirects the user to a frontend webpage or handles any errors.

    Notes:
        - The authorization code is extracted from the request URL.
        - Access and refresh tokens are obtained by making a POST request to Spotify's token
          endpoint.
        - Tokens are stored using the `update_or_create_user_tokens` utility.
    """
    load_dotenv()
    code = request.GET.get('code')
    returned_state = request.GET.get('state')
    stored_state = request.session.get('spotify_auth_state')
    print('code', code)

    if returned_state != stored_state:
        return HttpResponse("Authentication Failed: State Mismatch")

    if not code:
        return HttpResponse("Authentication Failed: Missing code parameter")

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': os.getenv('REDIRECT_URI'),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET')
    }, timeout=10).json()

    if 'error' in response:
        return HttpResponse(f"Authentication Failed: {response['error']}")

    # if not request.session.exists(request.session.session_key):
    #     request.session.create()
    # session_id = request.session.session_key

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    username = request.user.username

    print('username', username, 'access token', access_token)

    # Add the user to database, or update user info
    # update_or_add_spotify_user(request, session_id)
    update_or_create_user_tokens(access_token=access_token,
                                 token_type=token_type, refresh_token=refresh_token,
                                 expires_in=expires_in, username=username)
    request.session.save() #explicit save

    # Redirect to the frontend dashboard page after successful authentication
    frontend_dashboard_url = 'http://localhost:3000/dashboard'  # Adjust this URL as needed
    return redirect(frontend_dashboard_url)


class IsAuthenticated(APIView):
    """
    Class-based view to check if the current user is authenticated with Spotify.

    This view verifies whether the user has valid Spotify tokens and is currently
    authenticated. It can be used to check if API calls to Spotify should be allowed
    for a user.

    Methods:
        get(self, request, format=None): 
            Handles GET requests and returns the authentication status of the user.
    """

    def get(self, request, format=None):
        """
        Handles GET request to check if the user is authenticated with Spotify.

        Uses the username to check if the user has valid tokens stored in the database.

        Parameters:
            request (HttpRequest): The HTTP request object.
            format: The format of the request data (default: None).

        Returns:
            Response (rest_framework.response.Response): 
                A JSON response indicating the authentication status (True/False).
        """
        try:
            key = request.user.username
            is_authenticated = is_spotify_authenticated(key)
        except Exception:
            is_authenticated = False
        return Response({'status':  is_authenticated}, status=status.HTTP_200_OK)

@ensure_csrf_cookie
def get_csrf_token(request):
    """Ensures that a CSRF token is set for frontend requests."""
    response = JsonResponse({"detail": "CSRF cookie set"})
    return response

def sign_in(request):
    """
    Authenticates and logs in the user.

    Validates user credentials and logs them into the application. Returns 
    an appropriate response based on authentication status.

    Parameters:
        request (HttpRequest): The HTTP request containing login form data.

    Returns:
        JsonResponse: JSON response with success or error messages.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            # print("Form is valid. Cleaned data:", form.cleaned_data)  # Debugging line
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if user authentication works as expected
            user = authenticate(request, username=username, password=password)
            if user:
                # print("User authenticated successfully")  # Debugging line
                login(request, user)
                return JsonResponse({'message': 'Login successful'}, status=200)

            # print("Authentication failed: invalid username or password")  # Debugging line
            return JsonResponse({'errors': {'login': 'Invalid username or password'}},
                                    status=400)

        # Print form errors if validation fails
        # print("Form errors:", form.errors)  # Debugging line
        return JsonResponse({'errors': form.errors}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=405)

# logout button will lead to this instead
def sign_out(request):
    """Logs out the user and returns a success message."""
    logout(request)
    # messages.success(request, f'You are now logged out.')
    return JsonResponse({'message': 'Logged Out'}, status=200)

import logging
logger = logging.getLogger('accounts')

@csrf_exempt
def sign_up(request):
    """
    Registers a new user, validates username and password criteria, and logs them in.

    Processes registration form data, checks for valid username and password length, 
    saves the new user, and logs them in if successful. Returns appropriate success or 
    error messages.

    Parameters:
        request (HttpRequest): The HTTP request containing registration form data.

    Returns:
        JsonResponse: JSON response with success or error messages.
    """

    print("Received signup request")  # Add print statements
    logger.info("Received signup request")
    
    if request.method == 'POST':
        try:
            print(f"Raw POST data: {request.POST}")  # Add print statements
            print(f"Request body: {request.body.decode('utf-8')}")
            
            form = RegisterForm(request.POST)
            username = form.data.get('username')
            password = form.data.get('password1')
            
            print(f"Processing signup for username: {username}")  # Add print
            
            # Basic validation
            if username is None or password is None:
                print("Missing required fields")  # Add print
                return JsonResponse({
                    'error': 'Missing required fields',
                    'details': {
                        'username': username is None,
                        'password': password is None
                    }
                }, status=400)

            try:
                # Form validation
                if not form.is_valid():
                    print(f"Form validation errors: {form.errors}")  # Add print
                    return JsonResponse({'errors': form.errors}, status=400)
                
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                
                login(request, user)
                print(f"Successfully created and logged in user: {username}")  # Add print
                return JsonResponse({'message': 'sign-up successful'}, status=200)
                
            except Exception as e:
                print(f"Error saving user: {str(e)}")  # Add print
                return JsonResponse({
                    'error': 'Failed to create user',
                    'details': str(e)
                }, status=500)
                
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # Add print
            import traceback
            print(f"Traceback: {traceback.format_exc()}")  # Add detailed traceback
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e),
                'trace': traceback.format_exc()
            }, status=500)
    
    print(f"Invalid request method: {request.method}")  # Add print
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_username(request):
    '''Gets the username of the user for frontend'''
    username = request.user.username
    return JsonResponse({'username': username})

def delete_account(request):
    '''Tries to delete the account of the user and user data'''
    try:
        user = request.user
        delete_user_data(user.username)
        user.delete()
        return JsonResponse({'message': 'Account successfully deleted'}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    except Exception as e:
        return JsonResponse({'error': e.message}, status=500)
