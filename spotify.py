import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import requests
import numpy as np
import re


def initialize_auth(cid,secret):
    scope = "playlist-modify-public"
    spa = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid,
                                               client_secret=secret,
                                               redirect_uri="http://localhost:9000",
                                               scope=scope))
    return spa
    


def make_playlist(spa, u_id, name, song_ids):
    playlist = spa.user_playlist_create(user=u_id, name=name)
    try:
        spa.playlist_add_items(playlist["id"], song_ids)
    except Exception as e:
        print(e)
        return
    