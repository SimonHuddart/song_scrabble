import os
import requests
from bs4 import BeautifulSoup
import re

GENIUS_API_TOKEN='N58t0vu51_G62y9vlsrxLwMwUNedUSiOgm1UHNL8HPx3GTMdVysiuu1MySRfSUBA'

letter_score = {"A":1,"B":3,"C":3,"D":2,"E":1,"F":4,"G":2,"H":4,"I":1,"J":8,"K":5,"L":1,"M":3,"N":1,"O":1,"P":3,"Q":10,"R":1,"S":1,"T":1,"U":1,"V":4,"W":4,"X":8,"Y":4,"Z":10}

punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''

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
    while True:
        try:
            print("Trying to scrape: " + url + "...")
            page = requests.get(url)
            html = BeautifulSoup(page.text, 'html.parser')
            lyrics = html.find('div', class_='lyrics').get_text()
        except AttributeError:
            continue
        break
    #remove identifiers like chorus, verse, etc
    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
    #remove empty lines
    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])         
    return lyrics

def write_lyrics_to_file(artist_name, song_count):
    f = open('lyrics.txt', 'wb')
    urls = request_song_url(artist_name, song_count)
    for url in urls:
        lyrics = scrape_song_lyrics(url)
        f.write(lyrics.encode("utf8"))
    f.close()
    num_lines = sum(1 for line in open('lyrics.txt', 'rb'))
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
       score = score + letter_score[letter]
    return score

def avg_scrabble_score(text_file):
    total_score=0
    word_count=0
    legal_word_count=0
    illegal_word_count=0
    best_word = ('a',1)

    for line in text_file:
        line = line.upper()
        line_list = line.split()

        for word in line_list:
            word_count += 1
            word_score = 0
          
            for char in word:
                if char in punc:
                    word = word.replace(char,"")

            if is_legal(word) == True:
                word_score = scrabble_score(word)
                total_score = total_score + word_score
                legal_word_count += 1

                if word_count == 1:
                    best_word = (word, word_score)
                elif word_score > int(best_word[1]):
                    best_word = (word, word_score)
                else:
                    pass

            else:
                illegal_word_count += 1

    avg_score = total_score/word_count 

    return (total_score, avg_score, word_count, legal_word_count, illegal_word_count, best_word[0], best_word[1])

def song_scrabble(artist = "The Beatles", song_count = 10, file_dir = ('lyrics.txt')):

    print("Enter Artist Name:")
    artist = input()
    if artist == '':
        artist = "The Beatles"

    print("Enter Number of Songs to Score:")
    song_count = input()
    if song_count == '':
        song_count = 5
    song_count = int(song_count)

    write_lyrics_to_file(artist, song_count)
    with open(file_dir, 'r') as file:
        stats = avg_scrabble_score(file)
        print("\n \n \n")
        print("Total Scrabble Score = " + str(stats[0]))
        print("Average Scrabble Score = " + str(stats[1]))
        print("Total Word Count = " + str(stats[2]))
        print("Percent Legal Words = " + str(stats[3]/stats[2]*100))
        print("Percent Illegal Words = " + str(stats[4]/stats[2]*100))
        print("Best Word and Best Word Score = " + stats[5] + " : " + str(stats[6]))

song_scrabble()

# DEMO

#print (is_legal("APPLE"))
#print (avg_scrabble_score("APPLE ORANGE \n GRAPE PEAR"))

# DEMO

#with open("lyrics.txt", 'r') as file:
#    print(avg_scrabble_score(file))

# DEMO  
#write_lyrics_to_file('Eminem', 2)

# DEMO
#print(scrape_song_lyrics('https://genius.com/Lana-del-rey-young-and-beautiful-lyrics'))

# DEMO
#request_song_url('Lana Del Rey',50)
