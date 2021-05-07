import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from pytube.cli import on_progress
import configparser
from youtube_search import YoutubeSearch
import re
import os

config=configparser.ConfigParser()
config.read('config.cfg')
client_id = config.get('SPOTIFY', 'CLIENT_ID')
client_secret = config.get('SPOTIFY', 'CLIENT_SECRET')
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=auth_manager)

# Album Functions : 

def get_album_tracks_data(album_url):
    """Gets Album Tracks Data from Spotify API taking in URL argument
    """
    return sp.album_tracks(album_url)


def reformat_album_data(album_track_data):
    """Reads through Album Track Data and returns a list of all tracks in following format:
    {song} By {author}
    """
    reformatted_album_tracks = []
    for track in album_track_data['items']:
        track_artist = track['artists'][0]['name']
        track_name = track['name']
        reformatted_album_tracks.append("{} By {}".format(track_name, track_artist))
    
    return reformatted_album_tracks


# Playlist Functions:

def get_playlist_tracks(playlist_url):
    """Gets all tracks in a spotify playlist that is public using Spotify API, taking in the URL.
    Credit to https://stackoverflow.com/a/39113522/6032128
    """
    results = sp.playlist_tracks(playlist_url)
    playlist_tracks = results['items']
    while results['next']:
        results = sp.next(results)
        playlist_tracks.extend(results['items'])
    return playlist_tracks


def reformat_playlist_tracks_data(playlist_tracks_data):
    """Reads through Playlist Track Data and returns a list of all tracks in following format:
    {song} By {author}
    """
    reformatted_playlist_tracks = []
    for track in playlist_tracks_data:
        artists = ' And '.join([artist['name'] for artist in track['track']['artists']])
        song_name = track['track']['name']
        reformatted_playlist_tracks.append("{} By {}".format(song_name, artists))
    
    return reformatted_playlist_tracks


# Youtube and Download Functions:

def search_and_download(search, location):
    """Searches the search parameter on Youtube, and downloads the first
    video found when searching
    """
    file_name = re.sub(r'[\\/*?:"<>|]',"",search)
    if file_name not in list_of_files_in_folder(location):
        first_video_url = "http://youtube.com/" + YoutubeSearch(search, max_results=1).videos[0]["url_suffix"]
        yt = YouTube(first_video_url, on_progress_callback=on_progress)
        yt.streams.filter(only_audio=True)[-1].download(output_path=location, filename=file_name)


#Functions for Main:

def list_of_files_in_folder(location):
    """Returns a list of files in a folder, without extensions"""
    list_of_files = [f[:-5] for f in os.listdir(location) if os.path.isfile(os.path.join(location, f))]
    return list_of_files


def download_list_of_tracks(list_of_tracks, download_location):
    """Downloads songs in spotify playlist by searching the name through Youtube"""
    for track in list_of_tracks:
        i = 0
        downloaded = False
        while i < 3 and not downloaded:
            try:
                search_and_download(track, download_location)
                downloaded = True
            except Exception as e:
                print(e)
            i += 1


# Main Function:

def main():
    download_location = input("Enter location to download: ")
    spotify_url = input("Enter Spotify URL: ")
    is_playlist_url = "playlist" in spotify_url
    if is_playlist_url:
        list_of_tracks = reformat_playlist_tracks_data(get_playlist_tracks(spotify_url))
        download_list_of_tracks(list_of_tracks, download_location)
    else:
        list_of_tracks = reformat_album_data(get_album_tracks_data(spotify_url))
        download_list_of_tracks(list_of_tracks, download_location)


if __name__ == "__main__":
    main()
