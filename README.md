# Music Recommendation Based on Query and Song Similarity
The goal of this project is to make finding music easier. I gathered lyrical data from the Genius API as well as audio feature data from the Spotify API, using different methods to create vectors and measure distance between each song to find similarities.
  
To run the program, either run the entire notebook, or run:  
`python3 playlist.py`  

## Data Collection
- Genius API
  -  To start, I downloaded a dataset from [kaggle](https://www.kaggle.com/datasets/pieca111/music-artists-popularity) that had over 1.4 million artists with information on the amount of their listeners, the type of music they made, etc. I used this to get the top 500 artists (sorting by listeners).
  -  The next step was to use the artist names in the dataset to make calls to the Genius API using the [lyricsgenius library](https://lyricsgenius.readthedocs.io/en/master/). For each artist, I grabbed their 5 most popular songs and added their lyrics to a txt file.
  -  This data is all available in data/data_with_spotify_ids.csv
 - Spotify API
  - After all of the lyrical/song data was in a dataframe, I used the song name to make calls to the [spotify api](https://spotipy.readthedocs.io/en/master/) to get each songs unique spotify id.
  - This id made future api calls very seamless, so I gathered the audio features 'danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', and 'tempo' for each song.
  - This data is all available in data/audio_and_lyric_data.csv.
  
## Similarity Measures
The program will ask if you want to use Lyric similarity or Song similarity:
- Lyric similarity  
  -  User inputs a query, could be a mood, favorite words, lyrics etc.
  -  The program will vectorize the query using [tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) as well as all the song lyrics.
  -  Each song will have its own vector, and it is compared to the query vector using [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity), the highest values correspond to the songs that are most closely related to the query.
- Song similarity
  - User inputs a song, if the song is in the data it will extract certain audio features, obtained from the spotify API, they are: 'danceability', 'energy', 'key', 'loudness', 'speechiness','acousticness','instrumentalness', 'liveness', 'valence', and 'tempo', and will make a vector with these values
  - Each song in the data has values for these features, so they all have an audio feature vector.
  - The query's audio vector is compared to all of the other songs audio vectors using [bray curtis distance](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.braycurtis.html) the closer the value is to 1, the more similar it is to the query song.

Using either of these methods will print out 20 songs that the specified measure suggests. Unfortuanately spotify authorization isn't working at the moment, but ideally this would create a public playlist through my account that a user could look up and listen to.

## Future Work  
- Troubleshoot spotify connection and get it up and running.
- Build a simple UI that can recommend music using my methods.
- Apply some more NLP methods to get better song recommendations.
- The dataset is setup to constantly grow as users add artists that aren't in the data, setting this up in a SQL database would be much more efficient.
  
