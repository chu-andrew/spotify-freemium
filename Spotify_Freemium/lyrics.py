import re
import requests
from azlyrics.azlyrics import agent
from bs4 import BeautifulSoup

headers = {'User-Agent': agent}


def lyric(artist, song):
    artist = re.sub(r'\W+', '', artist)
    artist = artist.lower().replace(" ", "")
    song = re.sub(r'\W+', '', song)
    song = song.lower().replace(" ", "")

    url = "https://www.azlyrics.com/lyrics/" + artist + "/" + song + ".html"

    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.content, "html.parser")
    lyrics = soup.find_all("div", attrs={"class": None, "id": None})
    if not lyrics:
        return False
    elif lyrics:
        lyrics = [x.getText() for x in lyrics]
        lyrics = lyrics[0].split("\n")
        return lyrics


def parse_korean(lyric):
    try:
        korean_index = lyric.index("[Korean:]")
    except ValueError:
        korean_index = -1

    try:
        translation_index = lyric.index("[English translation:]")
    except ValueError:
        translation_index = -1

    if korean_index >= 0:
        if translation_index >= 0:
            return lyric[korean_index + 2:translation_index - 1]
        else:
            return lyric[korean_index + 2:]
    else:
        return lyric


def print_lyrics(artist, song):
    if artist[0:4] == "The ":
        artist = artist[4:]
    lyrics = lyric(artist, song)
    if lyrics:
        lyrics = parse_korean(lyrics)
        for line in lyrics:
            print(line)
        return True
    else:
        return False


if __name__ == '__main__':
    print_lyrics("", "")
