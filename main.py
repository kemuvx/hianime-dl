import time

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import m3u8_To_MP4
import re
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from seleniumbase import Driver


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

class Main:
    def __init__(self):

        user_search = input("Enter an anime name: ")
        self.anime_search_url = "https://hianime.to/search?keyword=" + user_search.replace(" ", "+")

        anime_search_page = requests.get(self.anime_search_url, headers=headers)

        search_soup = BeautifulSoup(anime_search_page.text, 'html.parser')
        main_content = search_soup.find('div', id='main-content')
        anime_names_h3 = main_content.find_all('h3')
        anime_links_a = main_content.find_all('a', class_="film-poster-ahref item-qtip")

        results_for_names = ""
        counter_for_names = 1
        for element in anime_names_h3:
            results_for_names += str(counter_for_names) + ": " + element.text + "\n"
            counter_for_names += 1

        results_for_links = ""
        counter_for_links = 1
        results_for_links_dict = {}
        for element in anime_links_a:
            results_for_links += str(counter_for_links) + " https://hianime.to" + element['href'] + "\n"
            results_for_links_dict[str(counter_for_links)] = "https://hianime.to" + element['href']
            counter_for_links += 1

        number_of_anime = int(input(results_for_names + "\nEnter the number of an anime you want to download: "))
        while number_of_anime <= 0 or number_of_anime > len(results_for_links_dict):
            print("Wrong number!")
            number_of_anime = int(input(results_for_names + "\nEnter the number of an anime you want to download: "))
        self.url_of_anime_watch = results_for_links_dict[str(number_of_anime)]
        print(self.url_of_anime_watch)

        self.getting_m3u8()

    def getting_m3u8(self):
        #fuck yeah mobile=True bypasses antibot on HiAnime
        driver = Driver(uc=True, headless=None, undetectable=True, mobile=True)

        driver.uc_open_with_reconnect(self.url_of_anime_watch, 3)
        time.sleep(90)




Main()
