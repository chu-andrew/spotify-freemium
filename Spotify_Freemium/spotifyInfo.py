# https://www.reddit.com/r/Python/comments/ga7y7f/i_made_a_little_program_that_mutes_spotify_ads/?utm_source=share&utm_medium=web2x
# https://github.com/MicRaj/Python-Projects/blob/a9c6d029060620887b83be9685e08b53a82ed363/AdMuter.py
# try deleting cache to debug

import time
import spotipy
import spotipy.util as util
from pycaw.pycaw import AudioUtilities
import dotenv
import os

import lyrics


def setup_spotify_object(username, scope, client_id, client_secret, redirect_uri):
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
    return spotipy.Spotify(auth=token)


dotenv.load_dotenv()

SPOTIPY_USERNAME = ""
SPOTIPY_ACCESS_SCOPE = "user-read-currently-playing"
SPOTIPY_CLIENT_ID = '6db5e4c011ab4bdb96821e346669fff7'
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "http://localhost:3000"


def main():
    if check_info()[0] == "#AD#":
        current_displayed = "#AD#"
    elif check_info()[0] == "closed":
        current_displayed = "closed"
    else:
        current_displayed = "first_track_placeholder"

    time_elapsed = 0  # limit the number of calls to api, but not at beginning of loop

    while True:
        current_check, current_song = check_info()  # since checkinfo returns array, set variables accordingly
        if current_check == "closed" or current_displayed == "closed":
            # can break if no spotify is detected,
            # but that would stop user from opening this app, then spotify
            time_elapsed = 0
            pass
        if current_check == "#AD#":
            mute_spotify_tab(True)
            time_elapsed = 0
        else:
            mute_spotify_tab(False)

            if current_displayed != current_song:
                if current_check != "closed":
                    info(current_check)
                    time_elapsed = 8
                current_displayed = current_song
            else:
                time_elapsed = time_elapsed * 0.50

        time.sleep(int(time_elapsed / 2 + 2))


def check_info():  # returns array of full info + name or array of AD + AD or array of closed + closed
    global spotifyObject

    try:
        track_info_check = spotifyObject.currently_playing()
    except Exception:
        print("Token Expired")
        spotifyObject = setup_spotify_object(SPOTIPY_USERNAME, SPOTIPY_ACCESS_SCOPE, SPOTIPY_CLIENT_ID,
                                             SPOTIPY_CLIENT_SECRET,
                                             SPOTIPY_REDIRECT_URI)
        track_info_check = spotifyObject.currently_playing()
    try:
        if track_info_check is None:
            return ["closed", "closed"]
        elif track_info_check["currently_playing_type"] == "ad":
            return ["#AD#", "#AD#"]
        elif track_info_check["currently_playing_type"] == "track":
            return [track_info_check, track_info_check["item"]["name"]]
    except Exception:
        pass


def info(track_info_for_print):
    if track_info_for_print["is_playing"]:

        url = track_info_for_print["item"]["album"]["images"][1]["url"]

        try:
            artist_for_lyric = track_info_for_print["item"]["artists"][0]["name"]
            song_for_lyric = track_info_for_print["item"]["name"]

            print()
            print("*" * 120)
            if lyrics.lyric(artist_for_lyric, song_for_lyric):
                print()
                print_lyrics(artist_for_lyric, song_for_lyric)

        except Exception:
            pass
        print()
        description = description_builder(track_info_for_print)
        ascii_art(url, description)  # print in format with ascii art


def description_builder(track_info_for_print):
    description = []

    song = track_info_for_print["item"]["name"]
    song = len_limit(song, "song")
    songs = song.split("\n")
    for line in songs:
        description.append(line)

    num_artists = len(track_info_for_print["item"]["artists"])
    if num_artists > 1:
        artists_str = ""
        for i in range(num_artists - 1):
            artists_str += track_info_for_print["item"]["artists"][i]["name"] + " | "
        artists_str += track_info_for_print["item"]["artists"][num_artists - 1]["name"]
        artists_str = len_limit(artists_str, "artists")
        artists = artists_str.split("\n")
        for line in artists:
            description.append(line)
    else:
        artists_str = "artist:\t"
        artists_str += track_info_for_print["item"]["artists"][num_artists - 1]["name"]
        description.append(artists_str)

    album_str = track_info_for_print["item"]["album"]["name"]
    album_str = len_limit(album_str, "album")
    album_str = album_str.split("\n")
    for line in album_str:
        description.append(line)

    return description


def print_lyrics(artist, song):
    import lyrics
    # import re
    # import requests
    # from azlyrics.azlyrics import agent
    # from bs4 import BeautifulSoup

    lyrics.print_lyrics(artist, song)


def len_limit(names, descriptor_type):
    limit = 36
    if descriptor_type == "artists":
        return len_limit_artist(names, limit)
    if len(names) > limit:
        fixed = ""
        current_len = 0
        names = names.split(" ")
        for i in range(len(names)):
            if current_len + len(names[i]) > limit:
                fixed += "\n\t\t\t"
                current_len = 0
            fixed += names[i] + " "
            current_len += len(names[i]) + 1
        if descriptor_type == "artists":
            return descriptor_type + ":\t" + fixed
        else:
            return descriptor_type + ":\t\t" + fixed
    if descriptor_type == "artists":
        return descriptor_type + ":\t" + names
    else:
        return descriptor_type + ":\t\t" + names


def len_limit_artist(names, limit):
    # needs different splitter due to multiple artists
    if len(names) > limit:
        fixed = ""
        current_len = 0
        names = names.split(" | ")
        for i in range(len(names)):
            if current_len + len(names[i]) + 2 > limit:
                fixed += "\n\t\t\t"
                current_len = 0
            fixed += names[i] + " | "
            current_len += len(names[i]) + 3
        return "artists:\t" + fixed[:-3]  # delete ending " | "
    return "artists:\t" + names


def ascii_art(url, strN):
    import colorama
    import ascii_magic

    colorama.init()

    ascii_cover = ascii_magic.from_url(url=url, columns=50, width_ratio=2,
                                       mode=ascii_magic.Modes.TERMINAL)

    ascii_cover = ascii_cover.split("\n")

    for i in range(len(ascii_cover)):
        start = 8
        if start <= i <= start + len(strN) - 1:
            print_ascii_str(ascii_cover[i])
            print(f'{colorama.Fore.WHITE} {strN[i - start]}')
        else:
            print(ascii_cover[i])


def print_ascii_str(ascii_cover):
    for i in range(len(ascii_cover)):
        print(ascii_cover[i], end="")
    print("\t\t", end="")  # controls space between album and description


def mute_spotify_tab(mute):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session.SimpleAudioVolume
        if session.Process and session.Process.name() == "Spotify.exe":
            if mute:
                volume.SetMute(True, None)
            else:
                volume.SetMute(False, None)


if __name__ == '__main__':
    spotifyObject = setup_spotify_object(SPOTIPY_USERNAME, SPOTIPY_ACCESS_SCOPE, SPOTIPY_CLIENT_ID,
                                         SPOTIPY_CLIENT_SECRET,
                                         SPOTIPY_REDIRECT_URI)
    main()
