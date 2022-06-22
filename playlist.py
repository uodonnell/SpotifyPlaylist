import pandas as pd
import numpy as np
import spotipy
from bs4 import BeautifulSoup
import requests
import sys
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance
from spotify import make_playlist, initialize_auth




def get_songs_from_lyrics(df, amnt):
    """
    Asks user for a query and uses tf-idf vectorization and cosine similarity
    to find songs with lyrics that most closely match te query.
    Returns the top {amnt} of songs.
    """
    query = input("Input your mood, favorite words, or favorite lyrics!")
    query = query.lower()
    q_ser = pd.Series([query])
    l_ser = pd.Series(df['lyrics_nostop'])

    q_lyrics = q_ser.append(l_ser)

    # the linear kernel is the dot product
    tf_idf = TfidfVectorizer().fit_transform(q_lyrics)
    # the query is the first item in the series, so compare it to the other items
    cosine_sim = cosine_similarity(tf_idf[0:1], tf_idf[1:]).flatten()
    top_songs_indices = cosine_sim.argsort()[:-amnt:-1]

    print(f"Songs that represent {query}\n")

    return df.iloc[top_songs_indices]

def get_query_song_info(daf, artist, song):
    """
    Get the artist name, song name and lyrics from given text.
    Updates the details dataframe.
    """
    artist_songs = daf[daf["artist_mb"] == artist.lower().strip()]
    song_info = daf[daf['song_name'] == song.lower().strip()]
    return pd.merge(artist_songs, song_info)

def song_sim(song1, song2):
    """
    Gets the distance between two songs, using a vector built of their
    audio features.
    """
    return distance.braycurtis(song1, song2)

def songs_with_similar_audio_features(track_info, amnt):
    """
    Asks user for a song, finds the song in data, if it doesn't exist then attempts to
    add it to data.
    Once the song is found, it extracts audio info, and measures distance to every other
    song in the data. 
    Returns top {amnt} closest songs
    """
    compare = ['danceability', 'energy', 'key', 'loudness', 'speechiness','acousticness', 
            'instrumentalness', 'liveness', 'valence', 'tempo']
    artist = input("Input an artists name: ")
    artist = artist.lower().strip()
    if not track_info['artist_mb'].str.contains(artist).any():
        print("That artist isn't in the database, let's try adding it!")
        add_new_songs()
    print("We have some songs from them!")
    songs = track_info[track_info["artist_mb"] == artist]
    for song in list(songs["song_name"]):
        print(song)
    song = input("Input one of their songs: ")

    result = get_query_song_info(track_info, artist, song)
    if result.empty:
        print("Looks like there was a problem, try again")
        return
    comp_query = result[compare]
    comp_query = comp_query.iloc[0]
    comp_query = comp_query.to_list()

    comp_df = track_info[compare]
    comp_df = comp_df.apply(pd.to_numeric)

    
    track_info["distance_from_query"] = comp_df.apply(lambda x : 
            song_sim(x.to_list(), comp_query), axis = 1)
    
    print(f"Songs that represent {song}\n")
    
    top_tracks = track_info.sort_values(by = ['distance_from_query'])

    return top_tracks.iloc[0:amnt+1]

def audio_similarity_spotify_ids(top_songs):
    """
    Simply returns spotify ids of songs to add to a playlist.
    """
    return list(top_songs["sp_id"])

def recommend(track_info):
    """
    Main driver of program user can choose:
        L - Find songs based on lyric similarity to a user-specified query
        S - Enter a song and find songs that are similar based on audio features
    Ideally, a spotify playlist would be created, but authoritazation isn't working
    """
    type_sim = input("Would you like to find similar songs based on a query (L) or song (S)?")
    if type_sim == 'S':
        top_songs = songs_with_similar_audio_features(track_info, 20)
    elif type_sim == 'L': 
        top_songs = get_songs_from_lyrics(track_info, 20)
    else:
        print("Not a valid option!")
        return
    print("Listen to these: \n")
    top_songs.apply(lambda x : print(f'{x["song_name"]} by {x["artist_mb"]}'), axis = 1)

    # this is where I would connect to spotify but there have been authoritization issues :(
    # make_pl = input("Would you like to make this a playlist? (y/n) ")
    # if make_pl == 'yes':
    #     name = input("Enter a name: ")
    #     ids = audio_similarity_spotify_ids(top_songs)
    #     sp = initialize_auth(cid, secret)
    #     u_id = '6046owg3hsttaxfq2ot19rrea'
    #     playlist, playlist_url = make_playlist(sp, uid, name, ids)
    #     print(f"Here you go! {playlist_url}")
    #     return
    # else:
    #     print("Thank you!")
    #     return


def main():
    track_info = pd.read_csv("audio_and_lyric_data.csv")
    recommend(track_info)


if __name__ == "__main__":
    main()




