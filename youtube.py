# 获取youtube直播的真实流媒体地址。
import requests
import re

class youtube:
    def __init__(self, url):
        if url.startswith('http'):
            if 'watch?v=' in url:
                self.handle = 'live/' + url.split('=')[-1]
            else:
                parts = url.split('/')
                supported_live_type = ['live', 'user', 'c', 'channel']
                if len(parts) < 2 or parts[-2] not in supported_live_type:
                    raise RuntimeError('Invalid youtube url.')
                self.handle = parts[-2] + '/' + parts[-1]
        else:
            self.handle = 'live/' + url

    def get_real_url(self):
        youtube_url = 'https://www.youtube.com/' + self.handle + '/live'
        header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
        }
        response = requests.get(url=youtube_url, headers=header, timeout=30)
        if response.status_code == 200:
            urls = re.findall('"hlsManifestUrl":"(.*\.m3u8)"', response.text)
        else:
            urls = []
        return urls


if __name__ == '__main__':
    url = input('输入youtube直播地址：\n')
    real_url = youtube(url).get_real_url()
    if real_url is not None:
        print(real_url)
    else:
        print('未开播或直播间不存在')
