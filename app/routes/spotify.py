from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
import requests
import os
from dotenv import load_dotenv
from app.utils.firestore import get_firestore_db

# Cargar las variables del archivo .env
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

spotify_bp = Blueprint('spotify', __name__)


@spotify_bp.route("/spotify/login")
def spotify_login():
    scope = "user-read-playback-state user-modify-playback-state playlist-modify-private playlist-read-private user-read-email user-read-recently-played"
    auth_url = (
        f"{SPOTIFY_AUTH_URL}?response_type=code"
        f"&client_id={SPOTIFY_CLIENT_ID}&redirect_uri={SPOTIFY_REDIRECT_URI}"
        f"&scope={scope}"
    )
    return redirect(auth_url)


@spotify_bp.route("/spotify/callback")
def spotify_callback():
    code = request.args.get("code")
    token_response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        },
    )
    tokens = token_response.json()
    session["access_token"] = tokens.get("access_token")
    return redirect(url_for("routes.spotify_player"))


@spotify_bp.route("/spotify/player")
def spotify_player():
    access_token = session.get("access_token")
    if not access_token:
        return "No access token available. Please log in again.", 401

    headers = {"Authorization": f"Bearer {access_token}"}

    profile_response = requests.get(f"{SPOTIFY_API_URL}/me", headers=headers)
    profile_data = profile_response.json() if profile_response.status_code == 200 else None

    playlists_response = requests.get(
        f"{SPOTIFY_API_URL}/me/playlists", headers=headers)
    playlists_data = playlists_response.json().get(
        "items", []) if playlists_response.status_code == 200 else []

    if not profile_data:
        return "No se pudo obtener el perfil del usuario. Por favor, inicia sesión nuevamente.", 500
    if not playlists_data:
        return "No se encontraron listas de reproducción. Por favor, verifica tu cuenta de Spotify.", 500

    return render_template("spotify/spotify_player.html", profile=profile_data, playlists=playlists_data, access_token=access_token)


@spotify_bp.route("/spotify/stats")
def user_stats():
    access_token = session.get("access_token")
    if not access_token:
        return "No token disponible. Por favor, inicia sesión.", 401

    headers = {"Authorization": f"Bearer {access_token}"}

    response_recently_played = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played?limit=50", headers=headers
    )

    response_top_tracks = requests.get(
        "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=50", headers=headers
    )

    tracks_by_month = {}

    if response_recently_played.status_code == 200:
        recently_played = response_recently_played.json().get("items", [])
        for item in recently_played:
            played_at = item["played_at"]
            track = item["track"]
            month = played_at[:7]
            if month not in tracks_by_month:
                tracks_by_month[month] = {}

            track_id = track["id"]
            tracks_by_month[month][track_id] = tracks_by_month[month].get(
                track_id, 0) + 1

    if response_top_tracks.status_code == 200:
        top_tracks = response_top_tracks.json().get("items", [])
        for track in top_tracks:
            album = track.get("album", {})
            release_date = album.get("release_date", "1900-01-01")
            month = release_date[:7]
            if month not in tracks_by_month:
                tracks_by_month[month] = {}

            track_id = track["id"]
            tracks_by_month[month][track_id] = tracks_by_month[month].get(
                track_id, 0) + 1

    sorted_tracks_by_month = {}
    for month, tracks in tracks_by_month.items():
        sorted_tracks = sorted(
            tracks.items(), key=lambda x: x[1], reverse=True
        )[:5]
        sorted_tracks_by_month[month] = sorted_tracks

    detailed_tracks_by_month = {}
    for month, tracks in sorted_tracks_by_month.items():
        detailed_tracks_by_month[month] = []
        for track_id, count in tracks:
            track_response = requests.get(
                f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers
            )
            if track_response.status_code == 200:
                detailed_tracks_by_month[month].append(track_response.json())

    return render_template("spotify/spotify_stats.html", tracks_by_month=detailed_tracks_by_month)
