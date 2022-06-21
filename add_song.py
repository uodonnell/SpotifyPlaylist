import lyricsgenius as lg
import pandas as pd
from pathlib import Path
from track_info import initialize_client, inject_song_id
from sklearn.feature_extraction.text import TfidfVectorizer
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import os


# private access key made for the purpose of this project, provided by Genius API
api_key = "70CRA8AP4tEP--ctvOaYW5epfCU-liVjkZpnhJaXBdiJu-ZZJNTSMIqExySO4NIq"

# initialize the genius object
genius = lg.Genius(api_key, skip_non_songs = True, remove_section_headers = True)
genius.timeout = 15 # time to fail if request isn't complete
genius.verbose = True # turn off verbose output, could be useful to debug though



def add_artist(artist):
    counter = 1
    # if 10 request fail in a row just stop
    while counter != 10:
        try:
            songs = (genius.search_artist(artist, max_songs = 5, sort = "popularity")).songs
            song_list = [song.lyrics for song in songs]
            count = 1
            for s in song_list:
                # write to file ex: Eminem_1 to the lyrics folder
                # The Strokes would be The%Strokes for easier splitting later
                with open(f"new_lyrics/{artist.replace(' ', '%')}_{count}", 'w') as out:
                    out.write(s)
                count += 1
            return
        except Exception as e:
            print(e)
            counter += 1
            continue

def extract_info(text, doc_name, details):
    # The format for Happy by Pharrell for example would be :
    # Happy Lyrics
    # {Song Lyrics}
    # Hence, we plit on 'Lyrics'
    try:
        song_name, lyrics = text.split('Lyrics', maxsplit= 1)
        #print(song_name)
    except Exception as e:
        #print(e)
        print(f"{doc_name} has no lyrics or had an error")
        return

    artist, _ = doc_name.rsplit('_', maxsplit = 1)
    details["artist_mb"].append(' '.join([str(elem) for elem in artist.split('%')]))
    details["song_name"].append(song_name)
    details["lyrics"].append(lyrics)

def read_docs(input_dir):
    details = {
        "artist_mb": [],
        "song_name": [],
        "lyrics": []
    }
    docs = os.listdir(input_dir)
    for doc in docs:
        #print(f"{input_dir}{doc}")
        with open(f"{input_dir}/{doc}") as f:
            doc_text = f.read()
            extract_info(doc_text, doc, details)
    df = pd.DataFrame(details)
    df["id"] = df.index
    return df

def remove_stopwords(df):
    stop = set()
    with open('data/stopwords.txt', 'r') as f:
        for line in f:
            stop.add(line.rstrip())

    df['lyrics_nostop'] = df['lyrics'].apply(lambda x: ' '.join(
        [word.lower() for word in x.split() if word not in (stop)]))
    
    return df

def add_tokens(df):
    analyze = TfidfVectorizer().build_analyzer()
    df['tokens'] = df['lyrics_nostop'].apply(analyze)
    df = df.drop(['lyrics'], axis=1)
    return df

def add_lyrics(sp,artist):
    add_artist(artist)
    print("Lyrics added in new files!")
    df = read_docs('new_lyrics/')
    df = remove_stopwords(df)
    df = add_tokens(df)
    df = inject_song_id(sp, df)
    return df

def add_audio_features(df,sp):
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
    track_info = pd.merge(df,track_info, on = "sp_id")
    
    return track_info

def update_df():
    df = pd.read_csv("data/audio_and_lyric_data.csv")
    return df

def add_new_songs():
    cid = '1d668be1930e487eaacd284df4fa7601'
    secret = '08ac712c04ba4bffaeb232efe98a7a54'
    sp = initialize_client(cid, secret)
    new_artist = input("Input artist you would like to add: ")
    print(new_artist)
    new_df = add_lyrics(sp, new_artist)
    newer_df = add_audio_features(new_df,sp)

    old_df = pd.read_csv("data/audio_and_lyric_data.csv")
    old_df = old_df.drop("Unnamed: 0", axis=1)
    print(old_df.columns)
    print(newer_df.columns)
    final_df = old_df.append(newer_df, ignore_index = True)
    final_df.to_csv("data/audio_and_lyric_data.csv")


# def main():
#     add_artist()


    

# if __name__ == "__main__":
#     main()


