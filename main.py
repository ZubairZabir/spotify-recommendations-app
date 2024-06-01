import os
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import spotipy

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Check if environment variables are set
if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    st.error("Please make sure all environment variables are set in the .env file.")
else:
    # Spotify Authentication
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="user-top-read"
        )
    )

    # Streamlit Configuration
    st.set_page_config(page_title="Spotify Dashboard", page_icon=":musical_note:")
    st.title("Analysis for your Top Songs")
    st.write("Discover insights about your Spotify listening habits.")

    # Fetch top tracks
    top_tracks = sp.current_user_top_tracks(limit=10, time_range="short_term")
    track_ids = [track["id"] for track in top_tracks["items"]]
    audio_features = sp.audio_features(track_ids)

    # Process audio features
    df = pd.DataFrame(audio_features)
    df["track_name"] = [track["name"] for track in top_tracks["items"]]
    df = df[["track_name", "danceability", "energy", "valence"]]
    df.set_index("track_name", inplace=True)

    # Display audio features
    st.subheader("Audio Features for Top Tracks")
    st.bar_chart(df, height=500)

    # Get recommendations based on top tracks
    recommendations = sp.recommendations(seed_tracks=track_ids[:5], limit=10)
    recommended_track_ids = [track["id"] for track in recommendations["tracks"]]
    recommended_tracks = sp.tracks(recommended_track_ids)["tracks"]

    # Process recommended tracks
    recommended_tracks_df = pd.DataFrame({
        "track_name": [track["name"] for track in recommended_tracks],
        "artist": [track["artists"][0]["name"] for track in recommended_tracks],
        "album": [track["album"]["name"] for track in recommended_tracks],
        "track_url": [track["external_urls"]["spotify"] for track in recommended_tracks]  # Add Spotify URL
    })

    # Convert track names to clickable links
    recommended_tracks_df["track_name"] = recommended_tracks_df.apply(
        lambda row: f'<a href="{row["track_url"]}" target="_blank">{row["track_name"]}</a>', axis=1
    )

    # Display recommended tracks with clickable links
    st.subheader("Recommended Tracks")
    st.write(recommended_tracks_df.to_html(escape=False), unsafe_allow_html=True)
    st.write("Enjoy these tracks based on your listening habits!")
