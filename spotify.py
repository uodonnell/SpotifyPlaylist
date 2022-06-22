import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import requests
import numpy as np
import re


def initialize_auth(cid,secret):
    """
    Initializes auth manager with POST access, for purpose of creating playlist.
    """
    scope = "playlist-modify-public"
    spa = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid,
                                               client_secret=secret,
                                               redirect_uri="http://localhost:8080",
                                               scope=scope))
    return spa
    


def make_playlist(spa, u_id, name, song_ids):
    """
    Creates a playlist on the account(u_id -> me!(Ulysses O'Donnell))
    with the given spotify song ids.
    """
    playlist = spa.user_playlist_create(user=u_id, name=name)
    playlist_id = playlist["id"]
    playlist_url = playlist["external_urls"]["spotify"]
    try:
        spa.playlist_add_items(playlist["id"], song_ids)
        return playlist_id, playlist_url
    except Exception as e:
        print(e)
        return
    

# for testing purposes!

def main():
    cid = '1d668be1930e487eaacd284df4fa7601'
    secret = '08ac712c04ba4bffaeb232efe98a7a54'
    spa = initialize_auth(cid,secret)
    u_id = '6046owg3hsttaxfq2ot19rrea'
    song_ids = ['2jZgzSxNSg1hTCq0ewWHGJ', '5XrfFo0JFOnWD9ZMNXGkQh', '4y1LsJpmMti1PfRQV9AWWe', '3by8IfnW9dZ2t4pZw1WVxz', '60nZcImufyMA1MKQY3dcCH', '3ZpQiJ78LKINrW9SQTgbXd', '5X8kkUaUlAyAUr9TYqDFTH', '60Ih7J2Q1o9shvMC2OAALu', '6kex4EBAj0WHXDKZMEJaaF', '6aPFJ2b6iApBxXHNFzzYAB', '26uDUal1TkjwwOaQQt1Uwy', '7o9uu2GDtVDr9nsR7ZRN73', '1IsGA5ceSC4a5nxgAEYnQd', '7jKsYUxH1F0WWV7nPSReRb']

    make_playlist(spa, u_id, "Happy Fun Times", song_ids)


if __name__ == "__main__":
    main()