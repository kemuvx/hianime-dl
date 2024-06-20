import shutil
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from seleniumbase import Driver
import os
import functions

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


class Main:
    def __init__(self):
        print(Fore.LIGHTGREEN_EX + "HiAnime " + Fore.LIGHTWHITE_EX + "downloader")

        functions.remove_trash_from_dir()

        name_of_anime = input("Enter the name of an anime: ")

        dict_with_anime_elements = functions.search_anime_and_get_elements_of_search_page_and_get_dict_of_them(name_of_anime)

        chosen_anime_dict = functions.select_anime_from_given_dict(dict_with_anime_elements)
        print(chosen_anime_dict)

        #selenium starts
        functions.scraping(chosen_anime_dict)
Main()
