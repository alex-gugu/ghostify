import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import requests
import random
BAR_LENGTH = 10

cid = [INSET CLIENT ID]
secret = [INSERT SECRRET]

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

def get_artist_lyrics(uri, name):
    #given the uri and name of an artist, returns all available lyrics
    albums = get_artist_albums(uri)
    all_tracks = []
    for album in albums:
        all_tracks += get_album_tracks(album)
    lyrics = lyrics_list(name, all_tracks)
    return lyrics
    

def get_artist_uri(name):
    #given name of an artist, searches spotify for artist uri and returns
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]['uri']
    else:
        return None

def get_artist_albums(uri):
    #given artist uri, returns uri of all their albums
    albums = []
    info = sp.artist_albums(uri, album_type = None, country = None, limit = None, offset = 0)
    for i in range(0, len(info['items']), 2):
        albums.append(info['items'][i]['uri'])
    return albums


def get_album_tracks(uri_info):
    #given uri of an album, returns list of tracks in that album

    track = []
    one = sp.album_tracks(uri_info, limit=50, offset=0, market='US')
    
    for i in range(len(one['items'])):
        track.append(one['items'][i]['name'])
    
    return track
    
def scrape_lyrics(artistname, songname):
    #given song and artist name, scrapes and returns lyrics from genius
    query = artistname + '-' + songname
    query = str(query.replace(' ','-')) if ' ' in query else str(query)

    page = requests.get('https://genius.com/'+ query + '-' + 'lyrics')
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics1 = html.find("div", class_="lyrics")
    lyrics2 = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")
    if lyrics1:
        lyrics = lyrics1.getText(separator="\n")
    elif lyrics2:
        lyrics = lyrics2.getText(separator="\n")
    elif lyrics1 == lyrics2 == None:
        lyrics = None
    return lyrics

def lyrics_list(artistname, tracks):
    #given a list of songs, returns a string of all the song lyrics
    lyrics = ""
    for trackname in tracks:
        lyric = scrape_lyrics(artistname, trackname)
        if lyric != None:
            lyrics += lyric
    return lyrics

def create_dic(ref_list):
    #takes in list of words and returns a dictionary mapping each word to a dictionary of subsequent words and their frequencies
    next_word = {}
    for i in range(len(ref_list) - 1):
        ref_list[i] = ref_list[i].lower()
    for i in range(len(ref_list) - 1):
        if ref_list[i] not in next_word:
            next_word[ref_list[i]] = {}
            next_word[ref_list[i]][ref_list[i + 1]] = 1
        elif ref_list[i+1] not in next_word[ref_list[i]]:
            next_word[ref_list[i]][ref_list[i + 1]] = 1
        else:
            next_word[ref_list[i]][ref_list[i + 1]] += 1
    return next_word

def select_next(map):
    #takes in a dictionary of words and frequencies and returns the word with the highest frequency
    top = 0
    for k,y in map.items():
        if y > top:
            key = k
            top = y
    return key

def select_next2(map):
    #takes in a dictionary of words and frequencies and returns a random word with a probability proportional to the frequency of the word
    sum = 0
    for y in map.values():
        sum += y
    rand = random.randint(1, sum)
    for k,y in map.items():
        rand -= y
        if rand <= 0:
            return k

def generate_sentence(dic, prompt, length):
    #takes in a prompt and iteratively generates a sentence using select_next to choose the next word, stops at length
    #if prompt is 'r', a random prompt is selected from dic
    if prompt == "r":
        prompt = random.choice(list(dic.keys()))
    result = prompt
    for i in range(length):
        next = select_next2(dic[prompt])
        result = result + " " + next
        prompt = next
    return result

def main():
    name = input("Please enter the name of an artist: ")
    if name == "quit program":
        quit()
    uri = get_artist_uri(name)
    while uri == None:
        name = input("Please try again: ")
        if name == "quit program":
            quit()
        uri = get_artist_uri(name)
    print("Retrieving lyrics...")
    lyrics = get_artist_lyrics(uri, name)
    ref_list = lyrics.split()
    print("Analyzing lyrics...")
    dic = create_dic(ref_list)
    
    prompt = input("Enter a prompt ('r': random,'q': quit, 'n': new prompt): ")
    while True:
        while prompt not in dic and prompt != "r":
            if prompt == "q":
                exit()
            prompt = input("Please enter a different prompt: ")
        inp = ""
        while inp != "n":
            print(generate_sentence(dic, prompt, BAR_LENGTH), end = " ")
            inp = input("")
        prompt = input("Enter a prompt: ")
    
    

if __name__ == "__main__":
    main()
