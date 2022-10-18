import json
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyPlaylistGenerator:
   """A spotify playlist generator class that generates 1-100 songs from a specified date"""

   def __init__(self) -> None:
      print("SPORTIFY PLAYLIST GENERATOR\n")
      
      self.user_id = None
      self.playlist_token = None
      self.is_public = True      
      self.spotify = None
      self.date = None

      self.playlist_id = None
      self.songs_count = None
      self.songs_list = None
      self.client_id = None
      self.client_secret = None

      try:
         self._set_tokens()
      except:
         self._get_tokens()


   def _set_tokens(self):
      with open('data.json', mode='r') as file:
         data = json.load(fp=file)
      
      self.user_id = data["user_id"]
      self.playlist_token = data["playlist_token"]
      self.is_public = data["is_public"]
      self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=data["client_id"], client_secret=data["client_secret"]))
         

   def _get_user_id(self):
      print("\nTIP: You can get your spotify user_id/username from https://www.spotify.com/us/account/overview/ ")
      user_id = ""
      while len(user_id) < 20:
         user_id = input("Enter your user_id/username ex. egnbqb281n6t7mxah0fbowo2k: \n")
      self.user_id = user_id


   def _get_is_public(self):
      user_option = input("\nShould the playlist be public 'yes' or 'no': \n")
      if user_option.lower() == 'yes':
         self.is_public = True
      else:
         self.is_public = False

   
   def _get_spotify_instance(self):
      print("\nTIP: You can get the client_id and client_secret keys from https://developer.spotify.com/dashboard/ \
         \n -> Login \n -> Create an App \n -> Copy client id & client secrete")
      self.client_id, self.client_secret = "", ""
      while len(self.client_id) < 20 and len(self.client_secret) < 20:
         client_id = input("Enter your client id: ")
         client_secret = input("Enter your client secret: ")

         self.client_id, self.client_secret = client_id, client_secret

      self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


   def _save_data(self):
      body = {
         "user_id": self.user_id,
         "playlist_token": self.playlist_token,
         "is_public": self.is_public,
         "client_id": self.client_id,
         "client_secret": self.client_secret,
      }
      with open(file='data.json', mode='w') as file:
         json.dump(obj=body, fp=file, indent=4)


   def _get_playlist_token(self):
      print("\nTIP: You can get a spotify playlist OAuth Token from https://developer.spotify.com/console/post-playlists/ \n \
         Note1: Make sure to toggle 'playlist-modify-public' and 'playlist-modify-private' before generating a token\n \
         Note2: Token Expires within an hour")

      playlist_token = ""
      while len(playlist_token) < 200:
         playlist_token = input("Enter your playlist OAuth Token: \n")
      print("loop broke")
      self.playlist_token = playlist_token


   def _get_tokens(self) -> None:
      """Get all the tokens required"""

      # Get user_id
      self._get_user_id()

      # Get playlist_token
      self._get_playlist_token()

      # Get is_public
      self._get_is_public()

      # Get spotify
      self._get_spotify_instance()
      
      # Create json file and add data
      self._save_data()


   def get_songs(self) -> list:
      """This function returns a list of the top from 1 - 100 billboard songs."""
      
      while True:
         try: 
            songs_count = int(input("How many songs would you like. 1-100: \n"))
            if songs_count > 0:
               self.songs_count = songs_count
               break
            raise Exception()
         except:
            print("Invalid amount. Try again.")

         
      # Date Input from user
      while True:
         date_input = input("Which year would you like to travel to? Type the date in this format YYYY-MM-DD: \n")
         if len(date_input) == 10:
            break
         print("Invalid date input. A proper format example would be 2009-03-24")


      self.date = date_input
      BILLBOARD_URL = f"https://www.billboard.com/charts/hot-100/{self.date}/"

      # Get top 100 songs title from BILLBOARD_URL
      r = requests.get(url=BILLBOARD_URL)
      soup = BeautifulSoup(r.text, "lxml")
      songs_list_html = soup.select(selector='li ul li h3')[:songs_count]
      self.songs_list = [song_html.getText().strip() for song_html in songs_list_html]
      return self.songs_list


   # Create playlist
   def create_playlist(self) -> None:
      """Creates a playlist on the provided spotify account"""
      
      SPORTIFY_CREATE_PLAYLIST_ENDPOINT = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"

      body = {
         "name": f"{self.date} Billboard 100",
         "description": "Once upon a time in my life",
         "public": self.is_public
      }

      # Create playlist with the header and body
      while True:
         try:
            r = requests.post(url=SPORTIFY_CREATE_PLAYLIST_ENDPOINT, headers=self._get_headers(self.playlist_token), json=body)
            self.playlist_id = r.json()["id"]
         except:
            print("Seems like your playlist token expired. Generate another one...")
            print(r.json())
            self._get_playlist_token()
            self._save_data()
         else:
            print("Playlist token worked")
            break

      print(f"Generating a Spotify Playlist with {self.songs_count} songs...")

      # Add tracks
      self._add_tracks()


   # Get Header
   def _get_headers(self, token : str) -> dict:
      """Returns a header dictionary object for authentication"""
      return {"Authorization": f"Bearer {token}"}


   # Add Tracks
   def _add_tracks(self) -> None:
      """Adds all tracks to the created playlist"""
      SPORTIFY_PLAYLIST_ADD_TRACK_ENDPOINT = f"https://api.spotify.com/v1/playlists/{self.playlist_id}/tracks"

      r = requests.post(url=SPORTIFY_PLAYLIST_ADD_TRACK_ENDPOINT, headers=self._get_headers(self.playlist_token), json=self._get_tracks())
      print("Playlist created successfully.")

   # Get Tracks
   def _get_tracks(self) -> list:
      """Returns a list of all the songs uris"""
      uris = []
      
      for track_name in self.songs_list:
         results = self.spotify.search(q='track:' + track_name, type='track')
         track_uri = results["tracks"]["items"][0]["uri"]
         uris.append(track_uri)
      
      return uris


