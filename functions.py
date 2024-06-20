import os
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from seleniumbase import Driver
def remove_trash_from_dir():
    try:
        os.remove('m3u8_To_MP4.mp4')
    except:
        pass
def get_rid_of_bad_chars(word_with_bad_chars):
    bad_chars = ['-', '.', '/', '\\', '?', '%', '*', '<', '>', '|', '"', "[", "]", ":"]
    for char in bad_chars:
        word_with_bad_chars = word_with_bad_chars.replace(char, '')
    return word_with_bad_chars
def search_anime_and_get_elements_of_search_page_and_get_dict_of_them(name_of_anime):
    def get_html_of_page(url):
        url = "https://hianime.to/search?keyword=" + url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    def get_anime_titles_from_page_and_make_dict_with_them(soup):
        main_content = soup.find('div', id='main-content')
        anime_elements = main_content.find_all('div', class_='flw-item')

        if not anime_elements:
            print("No anime found")
            quit()

        dict_with_anime_elements = {}
        counter_for_anime_titles = 1
        for element in anime_elements:
            name_of_anime = get_rid_of_bad_chars(element.find('h3', class_='film-name').text)
            url_of_anime = "https://hianime.to" + element.find('a', class_='film-poster-ahref item-qtip')['href']
            sub_episodes_available = element.find('div', class_="tick-item tick-sub").text
            try:
                dub_episodes_available = element.find('div', class_="tick-item tick-dub").text
            except:
                dub_episodes_available = "no"

            dict_with_anime_elements[counter_for_anime_titles] = {
                'name': name_of_anime,
                'url': url_of_anime,
                'sub_episodes': sub_episodes_available,
                'dub_episodes': dub_episodes_available
            }
            counter_for_anime_titles += 1
        return dict_with_anime_elements
    content_from_anime_search_page = get_html_of_page(name_of_anime)
    dict_with_anime_elements = get_anime_titles_from_page_and_make_dict_with_them(content_from_anime_search_page)
    return dict_with_anime_elements
def select_anime_from_given_dict(dict_with_anime_elements):
    for i in range(len(dict_with_anime_elements)):
        el = dict_with_anime_elements[i + 1]
        print(
            Fore.LIGHTRED_EX + str(i + 1) + ": " + Fore.LIGHTCYAN_EX + el['name'] + Fore.WHITE + ""
                                                                                                 " | " + "Episodes: " +
            Fore.LIGHTYELLOW_EX + str(
                el['sub_episodes']) + Fore.LIGHTWHITE_EX + " sub" + Fore.LIGHTGREEN_EX + " / "
            + Fore.LIGHTYELLOW_EX + str(el['dub_episodes']) + Fore.LIGHTWHITE_EX + " dub")
        number_of_anime = int(input("\nSelect an anime you want to download: "))
        dict_with_info_of_given_anime = dict_with_anime_elements[number_of_anime]
        return dict_with_info_of_given_anime











def get_urls_to_animes_from_html(html_of_page):
    urls_for_episodes = []
    soup = BeautifulSoup(html_of_page, 'html.parser')
    first_link = soup.find('div', id='episodes-content').find('a', class_='ssl-item ep-item active')
    urls_for_episodes.append("https://hianime.to" + first_link.get('href'))
    links = soup.find('div', id='episodes-content').find_all('a', class_='ssl-item ep-item')
    for link in links:
        urls_for_episodes.append("https://hianime.to" + link.get('href'))

    for url in urls_for_episodes:
        print(url)

def scraping(chosen_anime_dict):
    try:
        driver = Driver(mobile=True, wire=True, headed=True,
                        extension_zip='extensions/CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_58_0_0.zip')

        print("Connecting to the website...\n")

        driver.get(chosen_anime_dict['url'])
        urls_for_episodes = get_urls_to_animes_from_html(driver.page_source)

        episode_counter = 1

        for url in urls_for_episodes:
            print(url)
            print(
                Fore.LIGHTGREEN_EX + "Get" + Fore.LIGHTWHITE_EX + f" m3u8 link to episode {counter_for_episodes}..." + Fore.LIGHTWHITE_EX)



























    except Exception as e:
        raise e
    finally:
        driver.quit()
        print(Fore.LIGHTWHITE_EX + "Driver closed")

