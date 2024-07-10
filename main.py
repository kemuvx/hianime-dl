import shutil
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json
import yt_dlp
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

def choose_resolution():
    print("\nChoose resolution:\n\n1. 1080p (FHD)\n2. 720p (HD)\n3. 360p (SD)\n")
    resolution_map = {1: 1080, 2: 720, 3: 360}
    while True:
        try:
            choice = int(input("Enter Choice: "))
            if choice in [1, 2, 3]:
                resolution_height = resolution_map[choice]
                return resolution_height
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number (1, 2, or 3).")

def get_rid_of_bad_chars(word):
    bad_chars = ['-', '.', '/', '\\', '?', '%', '*', '<', '>', '|', '"', "[", "]", ":"]
    for char in bad_chars:
        word = word.replace(char, '')
    return word

def get_urls_to_animes_from_html(html_of_page, start_episode, end_episode):
    episode_info_list = []
    soup = BeautifulSoup(html_of_page, 'html.parser')
    
    # Find all episode links with the attribute data-number
    links = soup.find_all('a', attrs={'data-number': True})
    
    for link in links:
        episode_number = int(link.get('data-number'))
        if start_episode <= episode_number <= end_episode:
            url = "https://hianime.to" + link['href']
            episode_title = link.get('title')
            episode_info = {
                'url': url,
                'number': episode_number,
                'title': episode_title,
                'M3U8': None  # Initialize M3U8 field as None
            }
            episode_info_list.append(episode_info)
    
    return episode_info_list

class Main:

    def __init__(self):
        print(Fore.LIGHTGREEN_EX + "HiAnime " + Fore.LIGHTWHITE_EX + "Downloader")

        # REMOVE TRASH
        try:
            os.remove('m3u8_To_MP4.mp4')
        except FileNotFoundError:
            pass

        name_of_anime = input("Enter Name of Anime: ")

        # GET ANIME ELEMENTS FROM PAGE
        url = "https://hianime.to/search?keyword=" + name_of_anime
        search_page_response = requests.get(url, headers=headers)
        search_page_soup = BeautifulSoup(search_page_response.content, 'html.parser')

        main_content = search_page_soup.find('div', id='main-content')
        anime_elements = main_content.find_all('div', class_='flw-item')

        if not anime_elements:
            print("No anime found")
            return  # Exit if no anime is found

        # MAKE DICT WITH ANIME TITLES
        dict_with_anime_elements = {}
        for i, element in enumerate(anime_elements, 1):
            name_of_anime = get_rid_of_bad_chars(element.find('h3', class_='film-name').text)
            url_of_anime = "https://hianime.to" + element.find('a', class_='film-poster-ahref item-qtip')['href']
            try:
                # Some anime have no subs
                sub_episodes_available = element.find('div', class_="tick-item tick-sub").text
            except AttributeError:
                sub_episodes_available = "no"
            try:
                dub_episodes_available = element.find('div', class_="tick-item tick-dub").text
            except AttributeError:
                dub_episodes_available = "no"

            dict_with_anime_elements[i] = {
                'name': name_of_anime,
                'url': url_of_anime,
                'sub_episodes': sub_episodes_available,
                'dub_episodes': dub_episodes_available}

        # PRINT ANIME TITLES TO THE CONSOLE
        for i, el in dict_with_anime_elements.items():
            print(
                Fore.LIGHTRED_EX + str(i) + ": " + Fore.LIGHTCYAN_EX + el['name'] + Fore.WHITE + " | " + "Episodes: " +
                Fore.LIGHTYELLOW_EX + str(el['sub_episodes']) + Fore.LIGHTWHITE_EX + " sub" + Fore.LIGHTGREEN_EX + " / " +
                Fore.LIGHTYELLOW_EX + str(el['dub_episodes']) + Fore.LIGHTWHITE_EX + " dub")

        # USER SELECTS ANIME
        number_of_anime = int(input("\nSelect an anime you want to download: "))
        chosen_anime_dict = dict_with_anime_elements[number_of_anime]

        # Display chosen anime details
        print(f"\nYou have chosen {chosen_anime_dict['name']}")
        print(f"URL: {chosen_anime_dict['url']}")
        print(f"Sub Episodes: {chosen_anime_dict['sub_episodes']}")
        print(f"Dub Episodes: {chosen_anime_dict['dub_episodes']}")

        download_type = 'sub'
        if chosen_anime_dict['dub_episodes'] != "no" and chosen_anime_dict['sub_episodes'] != "no":
            download_type = input(
                "\nBoth sub and dub episodes are available. Do you want to download sub or dub? (Enter 'sub' or 'dub'): ").strip().lower()
            while download_type not in ['sub', 'dub']:
                print("Invalid choice. Please enter 'sub' or 'dub'.")
                download_type = input(
                    "\nBoth sub and dub episodes are available. Do you want to download sub or dub? (Enter 'sub' or 'dub'): ").strip().lower()

        elif chosen_anime_dict['dub_episodes'] == "no":
            print("Dub episodes are not available. Defaulting to sub.")
        else:
            print("Sub episodes are not available. Defaulting to dub.")
            download_type = "dub"

        # Get starting and ending episode numbers
        if chosen_anime_dict[f"{download_type}_episodes"] != "1":
            start_episode = int(input("Enter the starting episode number: "))
            end_episode = int(input("Enter the ending episode number: "))
        else:
            start_episode = 1
            end_episode = 1

        # CHROME DRIVER
        try:
            print("Opening chrome driver...")
            driver = Driver(mobile=True, wire=True, headed=True,
                            extension_zip='extensions/CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_58_0_0.zip')

            # CONNECT TO THE HIANIME
            print("Connecting to the website...\n")
            driver.get(chosen_anime_dict['url'])

            # Select sub or dub server based on user choice
            if download_type == 'sub':
                server_button_xpath = "//div[@class='ps_-block ps_-block-sub servers-sub']//a[contains(text(), 'HD-1')]"
            else:
                server_button_xpath = "//div[@class='ps_-block ps_-block-sub servers-dub']//a[contains(text(), 'HD-1')]"

            try:
                # Wait until the button is present in the DOM and visible
                server_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, server_button_xpath))
                )
                
                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", server_button)
                
                # Attempt to click the button
                server_button.click()
            except Exception as e:
                # Handle click interception
                print(f"Error selecting server: {e}")
                
                # Attempt to find and remove overlay
                try:
                    overlay_element = driver.find_element(By.XPATH, "//div[contains(@style, 'z-index: 2147483647')]")
                    driver.execute_script("arguments[0].style.display='none'", overlay_element)
                except Exception as e:
                    print(f"No overlay found to remove: {e}")
                
                # Try clicking the button again
                server_button.click()

            # GET URLS OF EPISODES
            episode_info_list = get_urls_to_animes_from_html(driver.page_source, start_episode, end_episode)
            
            # START SCRAPING URI'S TO .M3U8 AND .VTT

            # LIST OF POSSIBLE SUBTITLES LANGUAGES
            lang_list = (
                'ita', 'jpn', 'pol', 'por', 'ara', 'chi', 'cze', 'dan', 'dut', 'fin', 'fre', 'ger', 'gre', 'heb', 'hun', 'ind',
                'kor', 'nob', 'pol', 'rum', 'rus', 'tha', 'vie', 'swe', 'spa', 'tur')

            used_vtt_uri_list = []
            used_m3u8_uri_list = []
            counter_for_reload_page = 0

            os.makedirs("m3u8_urls", exist_ok=True)
            os.makedirs("vtt_files/" + chosen_anime_dict['name'], exist_ok=True)

            
            for episode in episode_info_list:
                url = episode['url']
                number = episode['number']
                title = episode['title']
                 
                print(Fore.LIGHTGREEN_EX + "Get" + Fore.LIGHTWHITE_EX + f" m3u8 link to Episode {number}..." + Fore.LIGHTWHITE_EX)
                driver.get(url)

                uri_to_m3u8_is_scraped = False
                uri_to_vtt_is_scraped = False
                max_retries = 5
                retry_count = 0
                start_time = None
                timeout_duration = 10  # Timeout duration in seconds

                while not (uri_to_m3u8_is_scraped and (uri_to_vtt_is_scraped or retry_count >= max_retries)):
                    driver.sleep(3)

                    # FIND M3U8 IN NETWORK REQUESTS
                    for request in driver.requests:
                        uri = request.url
                        try:
                            if uri.endswith('master.m3u8') and uri_to_m3u8_is_scraped is False and uri not in used_m3u8_uri_list and "biananset" in uri:
                                print('Found uri to master.m3u8: ' + uri)
                                uri_to_m3u8_is_scraped = True
                                used_m3u8_uri_list.append(uri)
                                episode['M3U8'] = uri
                        except Exception as e:
                            print(f"Error processing URI: {uri}, {e}")
                            
                    # FIND VTT IN NETWORK REQUESTS
                    start_time = time.time()
                    for request in driver.requests:
                        uri = request.url
                        if uri.endswith(".vtt") and "thumbnails" not in uri and not uri_to_vtt_is_scraped and not any(ele in uri for ele in lang_list) and uri not in used_vtt_uri_list:
                            print("Found uri to vtt: " + uri)
                            used_vtt_uri_list.append(uri)
                            uri_to_vtt_is_scraped = True
                            with open(os.path.join("vtt_files", chosen_anime_dict['name'], f"{chosen_anime_dict['name']} - Episode {number} - {title}.vtt"), 'wb') as subs_file:
                                content_of_uri = requests.get(uri, headers=headers).content
                                subs_file.write(content_of_uri)

                    # Check for timeout
                    if time.time() - start_time > timeout_duration:
                        print(f"Timeout reached for Episode {number}, proceeding without VTT.")
                        uri_to_vtt_is_scraped = True
                    retry_count += 1
                    
                counter_for_reload_page += 1
                if counter_for_reload_page == 5:
                    counter_for_reload_page = 0
                    driver.get(url)
        except Exception as e:
            raise e
        finally:
            driver.quit()
            print("Driver closed")
            
        os.makedirs("json", exist_ok=True)
        json_filename = os.path.join("json", f"{chosen_anime_dict['name']}.json")
        with open(json_filename, 'w') as f:
            json.dump(episode_info_list, f, indent=4)
            print(f"\nEpisode information exported to {json_filename}")
    
        # DOWNLOAD MP4 FROM M3U8
        download_or_no = input("Do you want to download the episodes?\nType 0 to exit: ")
        if download_or_no == "0": quit(0)
        
        folder_name = chosen_anime_dict['name']
        output_folder = os.path.join('./mp4_out', folder_name)
        os.makedirs(output_folder, exist_ok=True)
        
        resolution_height = choose_resolution()
        print(f"You chose: {resolution_height}p resolution\n")
        print(f"\nOutput Folder: {output_folder}\n\n")
        
        try:
            ydl = yt_dlp.YoutubeDL()            
            for episode in episode_info_list:
                url = episode['M3U8']
                number = episode['number']
                title = episode['title']

                ydl_opts = {
                    'no_warnings': True,
                    'quiet': True,
                    'outtmpl': os.path.join(output_folder, f"{folder_name} - Episode {number} - {title}.mp4"),
                    'format': f'bestvideo[height<={resolution_height}]+bestaudio/best[height<={resolution_height}]',
                }
                print(f"Downloading {folder_name} - Episode {number} - {title}.mp4.")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                print(f"Downloaded {folder_name} - Episode {number} - {title}.mp4 successfully.\n")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    Main()
