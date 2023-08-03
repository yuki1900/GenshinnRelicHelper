import requests
import urllib
from bs4 import BeautifulSoup
res = requests.get('https://bbs.mihoyo.com/ys/strategy/channel/map/37/39?bbs_presentation_style=no_header')
soup = BeautifulSoup(res.text,'html.parser')
divs = soup.find_all('a')
for div in divs:
    print(div)
    # if 'class' in div.attrs.keys() and div['class'] == "collection-avatar__icon":
    #     print(div['data-src'])


class DownLoader:
    def __init__(self):
        pass
    def down_load_with_url(self, url : str):
        pass

class Crawler:
    def __init__(self):
        pass
