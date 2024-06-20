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

        try:
            os.remove('m3u8_To_MP4.mp4')
        except:
            pass

        self.scrape_titles_from_search_page()
        self.select_title()
        self.scrape_m3u8_playlists_from_anime()
        self.m3u8_to_mp4()

    def scrape_titles_from_search_page(self):
        def search_anime():
            user_search = input(Fore.LIGHTWHITE_EX + "Enter an anime name: ")
            self.anime_search_url = "https://hianime.to/search?keyword=" + user_search.replace(" ", "+")
            anime_search_page = requests.get(self.anime_search_url, headers=headers)
            return anime_search_page
        anime_search_page = search_anime()
        search_soup = BeautifulSoup(anime_search_page.text, 'html.parser')
        main_content = search_soup.find('div', id='main-content')
        anime_elements = main_content.find_all('div', class_='flw-item')

        if not anime_elements:
            print("No anime found")
            Main()

        counter_for_animes = 1
        self.anime_elements_dict = {}
        for element in anime_elements:

            anime_name = element.find('h3', class_='film-name').text
            bad_chars = ['-', '.', '/', '\\', '?', '%', '*', '<', '>', '|', '"', "[", "]", ":"]
            for char in bad_chars:
                anime_name = anime_name.replace(char, '')

            anime_link = "https://hianime.to" + element.find('a', class_='film-poster-ahref item-qtip')['href']
            sub_episodes_available = element.find('div', class_="tick-item tick-sub").text
            try:
                dub_episodes_available = element.find('div', class_="tick-item tick-dub").text
            except:
                dub_episodes_available = "no"

            self.anime_elements_dict[counter_for_animes] = {
                'name': anime_name,
                'link': anime_link,
                'sub_episodes': sub_episodes_available,
                'dub_episodes': dub_episodes_available
            }
            counter_for_animes += 1

    def select_title(self):
        for i in range(len(self.anime_elements_dict)):
            el = self.anime_elements_dict[i + 1]
            print(
                Fore.LIGHTRED_EX + str(i + 1) + ": " + Fore.LIGHTCYAN_EX + el['name'] + Fore.WHITE + ""
                                                                                                     " | " + "Episodes: " +
                Fore.LIGHTYELLOW_EX + str(
                    el['sub_episodes']) + Fore.LIGHTWHITE_EX + " sub" + Fore.LIGHTGREEN_EX + " / "
                + Fore.LIGHTYELLOW_EX + str(el['dub_episodes']) + Fore.LIGHTWHITE_EX + " dub")

        self.number_of_anime = int(input("\nSelect an anime you want to download: "))
        if self.number_of_anime == 0:
            Main()
        self.url_of_anime_watch = self.anime_elements_dict[self.number_of_anime]['link']

    def scrape_m3u8_playlists_from_anime(self):
        self.m3u8_link = None
        self.sub_link = None
        try:
            print("Opening chrome driver...")

            driver = Driver(mobile=True, wire=True, headed=True, extension_zip='extensions/CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_58_0_0.zip')
            print("Connecting to the website...\n")

            driver.get(self.url_of_anime_watch)


            urls_for_episode_pages = []
            webpage = driver.page_source
            soup = BeautifulSoup(webpage, 'html.parser')
            first_link = soup.find('div', id='episodes-content').find('a', class_='ssl-item ep-item active')
            urls_for_episode_pages.append("https://hianime.to"+ first_link.get('href'))
            links = soup.find('div', id='episodes-content').find_all('a', class_='ssl-item ep-item')
            for link in links:
                urls_for_episode_pages.append("https://hianime.to"+ link.get('href'))

            for url in urls_for_episode_pages:
                print(url)



            self.uri_links = []
            used_urls = []
            used_sub_urls = []
            counter_for_subs = 1
            counter_for_episodes = 1
            sub_url_already_scraped = False
            os.makedirs('m3u8_urls', exist_ok=True)

            with open("m3u8_urls/" + self.anime_elements_dict[self.number_of_anime]['name'] + ".txt", 'w') as file:
                for url in urls_for_episode_pages:
                    print(url)
                    driver.get(url)
                    print(Fore.LIGHTGREEN_EX + "Get" + Fore.LIGHTWHITE_EX + f" m3u8 link to episode {counter_for_episodes}..." + Fore.LIGHTWHITE_EX)

                    counter_for_f5 = 0
                    while self.m3u8_link is None and self.sub_link is None:
                        driver.sleep(1.5)

                        for request in driver.requests:
                            if request.url.endswith(
                                    '.m3u8') and "index" in request.url and request.url not in used_urls:
                                used_urls.append(request.url)
                                self.m3u8_link = request.url
                                file.write("ep" + str(counter_for_episodes) + ": " + self.m3u8_link + "\n")
                                sub_url_already_scraped = False
                            elif request.url.endswith('.vtt') and "thumbnails" not in request.url and sub_url_already_scraped is False and request.url not in used_sub_urls:
                                os.makedirs(f'subs_for_anime/' + self.anime_elements_dict[self.number_of_anime]['name'], exist_ok=True)
                                with open(f"subs_for_anime/" + self.anime_elements_dict[self.number_of_anime]['name'] +"/" + self.anime_elements_dict[self.number_of_anime]['name'] + " subs " + "ep" +str(counter_for_subs) + ".vtt", 'wb') as subs_file:
                                    r = requests.get(request.url, headers=headers)
                                    used_sub_urls.append(request.url)
                                    subs_file.write(r.content)
                                    sub_url_already_scraped = True
                        counter_for_f5 += 1
                        if counter_for_f5 > 5:
                            driver.get(url)
                            counter_for_f5 = 0

                    self.uri_links.append(self.m3u8_link)
                    self.m3u8_link = None
                    self.sub_link = None

                    counter_for_f5 = 0
                    counter_for_subs += 1
                    counter_for_episodes += 1
                    driver.sleep(1)


        except Exception as e:
            raise e
        finally:
            file.close()
            driver.quit()
            print(Fore.LIGHTWHITE_EX + "Driver closed")

    def m3u8_to_mp4(self):
        import m3u8_To_MP4
        folder_name = self.anime_elements_dict[self.number_of_anime]['name'] + "/"
        os.makedirs('./mp4_out/' + folder_name, exist_ok=True)
        i = 1
        for uri in self.uri_links:
            print(Fore.LIGHTYELLOW_EX + "\nDownloading episode " + str(i) + Fore.WHITE)
            m3u8_To_MP4.multithread_download(uri)
            name = self.anime_elements_dict[self.number_of_anime]['name'] + " ep" + str(i) + ".mp4"
            folder_name = self.anime_elements_dict[self.number_of_anime]['name'] + "/"
            os.rename("m3u8_To_MP4.mp4", name)
            shutil.move(name, "./mp4_out/" + folder_name + name)
            print(Fore.LIGHTYELLOW_EX + "\nEpisode " + str(i) + " has been downloaded" + Fore.WHITE)
            i += 1


Main()
