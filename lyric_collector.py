import lyricsgenius as lg
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# private access key made for the purpose of this project, provided by Genius API
api_key = "Oj7CQ57mbgjqE8haUvFpv-dNED8YdZ15IA6uLv7YHTrbEfJzylBKsO6GmqwYovad"

# initialize the genius object
genius = lg.Genius(api_key, skip_non_songs = True, remove_section_headers = True)
genius.timeout = 15 # time to fail if request isn't complete
genius.verbose = False # turn off verbose output, could be useful to debug though


# call this once to build top_artists.csv file that is much smaller than original dataframe
def get_top_artists():
    """
    This function reads in top artist data from kaggle dataset, extracting specific
    columns that will be helpful.

    Additionally it will build a visualization for the types of music present in the data.
    """
    # source of data : https://www.kaggle.com/datasets/pieca111/music-artists-popularity
    all_artists = pd.read_csv("artists.csv", low_memory = False)
    # get rid of artists that have the same name
    all_artists = all_artists[all_artists["ambiguous_artist"] == False]
    all_artists = all_artists.sort_values(by=['listeners_lastfm'], ascending=False)
    
    # Visualization
    some = all_artists[:500]
    tags_ = some["tags_lastfm"].to_list()
    tag_dict = {}
    for item in tags_[1:]:
        if type(item) == str:
            tags = item.split(';')
            for tag in tags:
                tag = tag.strip()
                if tag in tag_dict:
                    tag_dict[tag] += 1
                else:
                    tag_dict[tag] = 1
    tag_dict = dict(sorted(tag_dict.items(), key=lambda x: x[1], reverse=True)[:20])
    plt.bar(tag_dict.keys(), tag_dict.values(), color='b')
    plt.xticks(rotation = 90)
    plt.tight_layout()
    plt.savefig("tags.png")


    # get artist name, and amount of listeners
    wanted = all_artists[['artist_mb', 'listeners_lastfm']]
    # sort by listeners, get rid of 0 and n/a values
    wanted = wanted.sort_values(by=['listeners_lastfm'], ascending=False)
    wanted = wanted[wanted["listeners_lastfm"] != 0.0]
    wanted = wanted.dropna()
    wanted.to_csv("top_artists.csv")


def get_top_artist_songs(artists):
    """
    Makes API calls to Genius and grabs lyrical information, storing each songs lyrics
    in a txt file
    """
    # functions as a queue because sometimes requests time out but sometimes they work
    # stop when failures exceed 40 or there are no artists left
    counter = 0
    while len(artists) != 0 and counter != 40:
        try:
            artist = artists.pop(0)
            songs = (genius.search_artist(artist, max_songs = 5, sort = "popularity")).songs
            song_list = [song.lyrics for song in songs]
            count = 1
            for s in song_list:
                # write to file ex: Eminem_1 to the lyrics folder
                with open(f"lyrics/{artist.replace(' ', '')}_{count}", 'w') as out:
                    out.write(s)
                count += 1
        except:
            print(f"Something wrong at {artist}")
            artists.append(artist)
            counter += 1
            continue


# def main():
#     # already have cleaned data but this function made it
#     # also produces visualization
#     get_top_artists()

#     artists = pd.read_csv("top_artists.csv")
#     # change iloc to 500:___ to get past the top 500 artists
#     get_top_artist_songs(artists["artist_mb"].iloc[0:500].to_list())



# if __name__ == "__main__":
#     main()