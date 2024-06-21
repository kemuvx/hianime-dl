import shutil
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from seleniumbase import Driver
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def replace_bad_num_in_m3u8_uri(url):
    right_part = url.split('index-f')[1][1:]
    return url.split('index-f')[0] + 'index-f' + right_part


def get_rid_of_bad_chars(word):
    bad_chars = ['-', '.', '/', '\\', '?', '%', '*', '<', '>', '|', '"', "[", "]", ":"]
    for char in bad_chars:
        word = word.replace(char, '')
    return word


def get_urls_to_animes_from_html(html_of_page):
    # GETS URI FROM HIANIME SEARCH PAGE TO EVERY ANIME

    urls_for_episodes = []
    soup = BeautifulSoup(html_of_page, 'html.parser')
    first_link = soup.find('div', id='episodes-content').find('a', class_='ssl-item ep-item active')['href']
    print(first_link)
    urls_for_episodes.append("https://hianime.to" + str(first_link))
    links = soup.find('div', id='episodes-content').find_all('a', class_='ssl-item ep-item')
    for link in links:
        urls_for_episodes.append("https://hianime.to" + link['href'])

    for url in urls_for_episodes:
        print(url)
    return urls_for_episodes


class Main:

    def __init__(self):
        print(Fore.LIGHTGREEN_EX + "HiAnime " + Fore.LIGHTWHITE_EX + "Downloader")

        # REMOVE TRASH
        try:
            os.remove('m3u8_To_MP4.mp4')
        except:
            pass

        name_of_anime = input("Enter Name of Anime: ")

        # GET ANIME ELEMENTS FROM PAGE
        url = "https://hianime.to/search?keyword=" + name_of_anime
        search_page_response = requests.get(url)
        search_page_soup = BeautifulSoup(search_page_response.content, 'html.parser')

        main_content = search_page_soup.find('div', id='main-content')
        anime_elements = main_content.find_all('div', class_='flw-item')

        if not anime_elements:
            print("No anime found")
            Main()

        # MAKE DICT WITH ANIME TITLES
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
                'dub_episodes': dub_episodes_available}
            counter_for_anime_titles += 1

        # PRINT ANIME TITLES TO THE CONSOLE
        for i in range(len(dict_with_anime_elements)):
            el = dict_with_anime_elements[i + 1]
            print(
                Fore.LIGHTRED_EX + str(i + 1) + ": " + Fore.LIGHTCYAN_EX + el[
                    'name'] + Fore.WHITE + " | " + "Episodes: " +
                Fore.LIGHTYELLOW_EX + str(
                    el['sub_episodes']) + Fore.LIGHTWHITE_EX + " sub" + Fore.LIGHTGREEN_EX + " / "
                + Fore.LIGHTYELLOW_EX + str(el['dub_episodes']) + Fore.LIGHTWHITE_EX + " dub")

        # USER SELECTS ANIME
        number_of_anime = int(input("\nSelect an anime you want to download: "))
        chosen_anime_dict = dict_with_anime_elements[number_of_anime]



        # CHROME DRIVER
        try:
            print("Opening chrome driver...")
            driver = Driver(mobile=True, wire=True, headless=True,
                            extension_zip='extensions/CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_58_0_0.zip')

            # CONNECT TO THE HIANIME
            print("Connecting to the website...\n")
            driver.get(chosen_anime_dict['url'])

            # GET URLS OF EPISODES
            urls_for_episodes = get_urls_to_animes_from_html(driver.page_source)

            # START SCRAPING URI'S TO .M3U8 AND .VTT

            # LIST OF POSSIBLE  SUBTITLES LANGUAGES
            lang_list = (
            'ita', 'jpn', 'pol', 'por', 'ara', 'chi', 'cze', 'dan', 'dut', 'fin', 'fre', 'ger', 'gre', 'heb', 'hun', 'ind',
            'kor', 'nob', 'pol', 'rum', 'rus', 'tha', 'vie', 'swe', 'spa', 'tur')

            episode_counter = 1
            used_vtt_uri_list = []
            used_m3u8_uri_list = []
            uri_links_list = []
            counter_for_reload_page = 0

            os.makedirs("m3u8_urls", exist_ok=True)
            os.makedirs("vtt_files/"+chosen_anime_dict['name'], exist_ok=True)

            # FILE WHERE LINKS TO M3U8 ARE WRITTEN m3u8_urls/some anime ep1.txt
            m3u8_links_file = open("m3u8_urls/" + chosen_anime_dict['name'] + " m3u8"+".txt", 'w')
            for url in urls_for_episodes:

                print(
                    Fore.LIGHTGREEN_EX + "Get" + Fore.LIGHTWHITE_EX + f" m3u8 link to episode {episode_counter}..." + Fore.LIGHTWHITE_EX)
                driver.get(url)

                uri_to_m3u8_is_scraped = False
                uri_to_vtt_is_scraped = False

                while not (uri_to_m3u8_is_scraped and uri_to_vtt_is_scraped):
                    driver.sleep(3)

                    # FIND M3U8 IN NETWORK REQUESTS
                    for request in driver.requests:
                        uri = request.url
                        try:
                            uri_without_f = replace_bad_num_in_m3u8_uri(uri)
                            if uri.endswith(
                                    '.m3u8') and 'index' in uri and uri_to_m3u8_is_scraped is False and uri_without_f not in used_m3u8_uri_list and uri_without_f is not None and "biananset" in uri:
                                uri_without_f = replace_bad_num_in_m3u8_uri(uri)
                                print('Found uri to m3u8: ' + uri)
                                uri_to_m3u8_is_scraped = True
                                m3u8_links_file.write("ep" + str(episode_counter) + ": " + uri + "\n")
                                used_m3u8_uri_list.append(uri_without_f)
                                uri_links_list.append(uri)
                        except:
                            pass





                    # FIND VTT IN NETWORK REQUESTS
                    for request in driver.requests:
                        uri = request.url
                        if uri.endswith(".vtt") and "thumbnails" not in uri and not uri_to_vtt_is_scraped and not any(ele in uri for ele in lang_list) and uri not in used_vtt_uri_list:
                            print("Found uri to vtt: "+uri)
                            used_vtt_uri_list.append(uri)
                            uri_to_vtt_is_scraped = True
                            with open("vtt_files/" + chosen_anime_dict['name'] + "/" +
                                      chosen_anime_dict['name'] + " subs " + "ep" + str(
                                    episode_counter) + ".vtt", 'wb') as subs_file:
                                content_of_uri = requests.get(uri, headers=headers).content
                                subs_file.write(content_of_uri)
                episode_counter += 1
                counter_for_reload_page += 1
                if counter_for_reload_page == 5:
                    counter_for_reload_page = 0
                    driver.get(url)
        except Exception as e:
            raise e
        finally:
            try:
                m3u8_links_file.close()
            except:
                pass

            driver.quit()
            print("Driver closed")

        # DOWNLOAD MP4 FROM M3U8
        download_or_no = input("Do you want to download m3u8 files now?\nType 0 to exit")
        if download_or_no == "0": quit(0)
        import m3u8_To_MP4
        folder_name = chosen_anime_dict['name'] + "/"
        os.makedirs('./mp4_out/' + folder_name, exist_ok=True)
        i = 1
        for uri in uri_links_list:
            print(Fore.LIGHTYELLOW_EX + "\nDownloading episode " + str(i) + Fore.WHITE)
            m3u8_To_MP4.multithread_download(uri)
            name = chosen_anime_dict['name'] + " ep" + str(i) + ".mp4"
            folder_name = chosen_anime_dict['name'] + "/"
            os.rename("m3u8_To_MP4.mp4", name)
            shutil.move(name, "./mp4_out/" + folder_name + name)
            print(Fore.LIGHTYELLOW_EX + "\nEpisode " + str(i) + " has been downloaded" + Fore.WHITE)
            i += 1


Main()
