import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

GENIUS_API_TOKEN='N58t0vu51_G62y9vlsrxLwMwUNedUSiOgm1UHNL8HPx3GTMdVysiuu1MySRfSUBA'

letter_score = {"A":1,"B":3,"C":3,"D":2,"E":1,"F":4,"G":2,"H":4,"I":1,"J":8,"K":5,"L":1,"M":3,"N":1,"O":1,"P":3,"Q":10,"R":1,"S":1,"T":1,"U":1,"V":4,"W":4,"X":8,"Y":4,"Z":10}

scrab_dict = open("scrab_dict.txt")
scrab_dict = scrab_dict.read().split()

# Get artist object from Genius API
def request_artist_info(artist_name, page):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
    search_url = base_url + '/search?per_page=10&page=' + str(page)
    data = {'q': artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    return response
# Get Genius.com song url's from artist object
def request_song_url(artist_name, song_cap):
    page = 1
    songs = []
    
    while True:
        response = request_artist_info(artist_name, page)
        json = response.json()
        # Collect up to song_cap song objects from artist
        song_info = []
        for hit in json['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_info.append(hit)
    
        # Collect song URL's from song objects
        for song in song_info:
            if (len(songs) < song_cap):
                url = song['result']['url']
                songs.append(url)
            
        if (len(songs) == song_cap):
            break
        else:
            page += 1
        
    print('Found {} songs by {}'.format(len(songs), artist_name))
    return songs
    
# Scrape lyrics from a Genius.com song URL
def scrape_song_lyrics(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    #remove identifiers like chorus, verse, etc
    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
    #remove empty lines
    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])         
    return lyrics

def write_lyrics_to_file(artist_name, song_count):
    f = open('lyrics/' + artist_name.lower() + '.txt', 'wb')
    urls = request_song_url(artist_name, song_count)
    for url in urls:
        lyrics = scrape_song_lyrics(url)
        f.write(lyrics.encode("utf8"))
    f.close()
    num_lines = sum(1 for line in open('lyrics/' + artist_name.lower() + '.txt', 'rb'))
    print('Wrote {} lines to file from {} songs'.format(num_lines, song_count))
  
def is_legal(word):
    if word in scrab_dict:
        return True
    else:
        return False

def scrabble_score(word):
    score = 0
    letters = list(word)
    for letter in letters:
       score = word_score + letter_score[letter]
    return score

def avg_scrabble_score(text_file):
    avg_score=0
    for line in text:
        line_score=0
        line_list = line.split()
        for word in line_list:
            word_score=0
            word = word.upper()
            if is_legal(word) == True:
                word_score = scrabble_score(word)
            else:
                line_list.remove(word)
            line_score = line_score + word_score
        line_count = len(line_list)
        avg_score = avg_score + line_score/line_count
    return avg_score



print (is_legal("APPLE"))
avg_scrabble_score("APPLE APPLE")


# DEMO  
#write_lyrics_to_file('Eminem', 10)

# DEMO
#print(scrape_song_lyrics('https://genius.com/Lana-del-rey-young-and-beautiful-lyrics'))

# DEMO
#request_song_url('Lana Del Rey',50)
