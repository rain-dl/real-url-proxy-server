# 获取youtube直播的真实流媒体地址。
import yt_dlp

class youtube:
    def __init__(self, url:str, cookiefile:str = None, proxy:str = None):
        if url.startswith('http'):
            self.youtube_url = url
        else:
            self.youtube_url = 'https://www.youtube.com/watch?v=' + url

        self.ydl_opts = {'quiet': True, 'extractor-args': 'youtube:player-client=web;formats=incomplete'}
        if cookiefile is not None:
            self.ydl_opts['cookiefile'] = cookiefile
        if proxy is not None:
            self.ydl_opts['proxy'] = proxy
        self.ydl = yt_dlp.YoutubeDL(self.ydl_opts)

    def get_real_url(self):
        try:
            info = self.ydl.extract_info(self.youtube_url, download=False)
            if 'manifest_url' in info:
                return [info['manifest_url']]
            if 'url' in info:
                return [info['url']]
            return []
        except Exception as e:
            print('Error: ' + str(e))
            return []


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Stream tester.')
    parser.add_argument('-p', '--proxy', type=str, nargs='?', default=None, help='Set the proxy server to use.')
    parser.add_argument('-k', '--cookie', type=str, nargs='?', default=None, help='Set the cookie file to use.')
    args = parser.parse_args()

    url = input('输入youtube直播地址：\n')
    real_url = youtube(url, args.cookie, args.proxy).get_real_url()
    if real_url is not None:
        print(real_url)
    else:
        print('未开播或直播间不存在')
