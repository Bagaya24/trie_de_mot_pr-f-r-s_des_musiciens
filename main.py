import json
from collections import Counter

import requests
from pprint import pprint
from bs4 import BeautifulSoup


def is_valid(word):
    if "[" in word and "]" in word:
        return False
    return True


def extract_lyrics(url):
    r = requests.get(url)
    if r.status_code != 200:
        return
    soup = BeautifulSoup(r.content, "html.parser")
    lyrics = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-5 Dzxov")
    if not lyrics:
        return extract_lyrics(url)
    all_words = []
    for sentence in lyrics.stripped_strings:
        sentence_words = [word.strip(",").strip(".").strip("(").strip(")").lower() for word in sentence.split() if is_valid(word)]
        all_words.extend(sentence_words)

    return all_words


def get_all_urls():
    page = 1
    link = []
    while page < 4:
        url = requests.get(f"https://genius.com/api/artists/45855/songs?page={page}&per_page=20&sort=popularity&text_format=html%2Cmarkdown")
        if url.status_code == 200:
            print(f"chargement de la page...{page}")
            response = url.json().get("response", {})
            #on met un dict vide comme ca si jamais response ne pas trouver, ca va nous retourne un discto vide et il n'y aura pas d'erreur
            next_page = response.get("next_page")
            songs = response.get("songs")
            link.extend([song.get("url") for song in songs])

            page += 1
            if not next_page:
                print("Plus de pages suivantes")
                break
    return link


def get_all_words():
    urls = get_all_urls()
    words = []
    for url in urls:
        lyrics = extract_lyrics(url=url)
        words.extend(lyrics)
    with open("data.json", "w") as f:
        json.dump(words, f, indent=4)
    counter = Counter(_ for _ in words if len(_) > 3)
    most_common_words = counter.most_common(10)
    pprint(most_common_words)


get_all_words()
