## Project description


## Usage

This is a simple spotify playlist generator

```python
from spotify_playlist_generator_100 import SpotifyPlaylistGenerator

spotify = SpotifyPlaylistGenerator()
songs_list = spotify.get_songs()
spotify.create_playlist()
```

This simple spotify playlist generator generates a playlist on your spotify account after being provided a series of validation tokens and keys from your spotify account, a date and a range of songs you want on your playlist.

The top 1-100 billboard chart songs are then generated and populated on your brand new spotify playlist

### Installation

Install from PyPi using pip, a package manager for Python.

```
$ python -m pip install spotify_playlist_generator_2
```