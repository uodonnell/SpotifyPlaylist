import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import requests
import numpy as np
import re


def initialize_client(cid,secret):
    """
    Creates a spotify api client, so I can access data from the API
    """
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    return sp

def search_for_song(sp, artist, song_name):
    """
    Searchs for a song and returns song ID of first song returned (most relevant result).
    :param sp: Spotify connection
    :param artist: Artist of the song in question.
    :param song_name: Name of the song in question.
    :return: the ID of the first song from Spotify's search.

    Credit : I was part of a school project that connected to the spotify API
    to create playlists, so I used some code from that.
    """
    query = "artist:" + artist + " track:" + song_name
    songs = sp.search(query, limit=1, type="track", market="US")
    if len(songs["tracks"]["items"]) == 0:
        return np.nan
    return songs["tracks"]["items"][0]["id"]

def clean_song(sp_id, song):
    """
    Gets rid of punctuation in the song name
    """
    # This checks for NoneType
    if sp_id == sp_id:
        return song
    new = re.sub(r'[^\w\s]', '', song)
    return new

def inject_song_id(sp, info):
    """
    Makes calls to spotify API to get the unique id of each song in the dataframe
    and inserts them into a new column into the dataframe.
    Any songs that were unsuccesful were removed from data.
    """
    info["sp_id"] = info.apply(lambda x: search_for_song(sp, x["artist_mb"], x["song_name"]), axis = 1)

    # Only 139 songs out of over 2000 have missing IDs, and many of them had punctuation, 
    # clean the songs that they couldn't find in spotify by removing punctuation
    # otherwise we can safely remove them from the dataframe
    info["song_name"] = info.apply(lambda x: clean_song(x["sp_id"], x["song_name"]), axis = 1)
    info['sp_id'] = info.apply(lambda x : x['sp_id'] if x["sp_id"] == x["sp_id"] 
                               else search_for_song(sp, x['artist_mb'], x['song_name']), axis = 1)
    # after this there were 79 missing id's, so I just removed them
    info = info.dropna(subset = ["sp_id"])
    return info


def get_track_info(sp, df):
    """
    This uses the spotipy library to grab information
    about the track that will help assemble some simmilarities
    between a query and a song.
    """
    track_info = {
        'sp_id': [],
        'danceability':[],
        'energy':[],
        'key':[],
        'loudness':[],
        'speechiness':[],
        'acousticness':[],
        'instrumentalness':[],
        'liveness':[],
        'valence':[],
        'tempo':[]
    }
    for i in df['sp_id']:
        # there was probably a much better way to do this but this is
        # what Im going with
        for x in sp.audio_features(tracks=[i]):
            track_info['sp_id'].append(i)
            for k,v in track_info.items():
                if k == 'sp_id':
                    continue
                try:
                    v.append(x[k])
                except:
                    v.append(np.nan)
            
    track_info = pd.DataFrame.from_dict(track_info)
    
    return track_info


# def main():
#     cid = '1d668be1930e487eaacd284df4fa7601'
#     secret = '08ac712c04ba4bffaeb232efe98a7a54'

#     info = pd.read_csv("data/data_with_spotify_ids.csv")
#     info = info.drop("Unnamed: 0",axis=1)
#     info = info.drop("Unnamed: 0.1",axis=1)
#     sp = initialize_client_spotify(cid, secret)
#     track_info = get_track_info(sp, info)
#     # there are one or two songs that dont have data on anything, so
#     # drop it based on one column, wont matter
#     track_info = track_info.dropna(subset = ["danceability"])
#     all_info = pd.merge(info, track_info, on = "sp_id")
#     all_info.to_csv("data/audio_and_lyric_data.csv")
    


# if __name__ == "__main__":
#     main()