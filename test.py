from seleniumbase import Driver
import time
import re
from pprint import pformat

url = 'https://hianime.to/watch/gosick-397?ep=8979'

driver = Driver( mobile=True, wire=True)
driver.get(url)

m3u8_link = None
try:
    driver = Driver(mobile=True, wire=True)
    driver.get(url)
    time.sleep(5)
    for request in driver.requests:
            if request.url.endswith('.m3u8'):
                m3u8_link = request.url
    print(m3u8_link)
    driver.quit()
    import m3u8_To_MP4
    m3u8_To_MP4.async_download(m3u8_link)
finally:
    driver.quit()


