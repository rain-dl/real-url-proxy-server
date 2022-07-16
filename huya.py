# 获取虎牙直播的真实流媒体地址。
# 虎牙"一起看"频道的直播间可能会卡顿
import requests
import re
import base64
import urllib.parse
import hashlib
import time
import json
import html

class huya:
    def __init__(self, rid, uid = 0, mode = 2):
        self.room_id = rid
        self.user_id = uid
        self.mode = mode
        self.live_url_infos = {}
        self.update_live_url_info()

    def decode_live_url_info(self, srcAntiCode):
        srcAntiCode = html.unescape(srcAntiCode)
        c = srcAntiCode.split('&')
        c = [i for i in c if i != '']
        n = {i.split('=')[0]: i.split('=')[1] for i in c}
        fm = urllib.parse.unquote(n['fm'])
        u = base64.b64decode(fm).decode('utf-8')
        live_url_info = {}
        live_url_info['hash_prefix'] = u.split('_')[0]
        live_url_info['uuid'] = n.get('uuid', '')
        live_url_info['ctype'] = n.get('ctype', '')
        live_url_info['txyp'] = n.get('txyp', '')
        live_url_info['fs'] = n.get('fs', '')
        live_url_info['t'] = n.get('t', '')
        return live_url_info

    def clear_live_url_infos(self):
        self.live_url_infos = {}

    def update_live_url_info(self):
        try:
            if self.mode == 0:
                room_url = 'https://m.huya.com/' + str(self.room_id)
                header = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/75.0.3770.100 Mobile Safari/537.36 '
                }
                response = requests.get(url=room_url, headers=header, timeout=30)
                if response.status_code == 200:
                    self.clear_live_url_infos()
                    livelineurl_base64 = re.findall(r'"liveLineUrl":"([\s\S]*?)"', response.text)[0]
                    if livelineurl_base64:
                        try:
                            livelineurl = str(base64.b64decode(livelineurl_base64), "utf-8")
                        except Exception:
                            livelineurl = livelineurl_base64
                        if 'replay' not in livelineurl:
                            url, anti_code = livelineurl.split('?')
                            live_url_info = {}
                            live_url_info['stream_name'] = re.sub(r'.(flv|m3u8)', '', url.split('/')[-1])
                            live_url_info['base_url'] = 'http:' + url.split('/' + live_url_info['stream_name'])[0]
                            live_url_info['hls_url'] = 'http:' + url
                            live_url_info.update(self.decode_live_url_info(anti_code))
                            self.live_url_infos['TX'] = live_url_info
            elif self.mode == 1:
                room_url = 'https://www.huya.com/' + str(self.room_id)
                header = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
                }
                response = requests.get(url=room_url, headers=header, timeout=30)
                if response.status_code == 200:
                    self.clear_live_url_infos()
                    liveData = None
                    streamInfo = re.findall(r'stream: ([\s\S]*?)\n', response.text)
                    if (len(streamInfo) > 0):
                        liveData = json.loads(streamInfo[0])
                    else:
                        streamInfo = re.findall(r'"stream": "([\s\S]*?)"', response.text)
                        if (len(streamInfo) > 0):
                            liveDataBase64 = streamInfo[0]
                            liveData = json.loads(str(base64.b64decode(liveDataBase64), 'utf-8'))
                    if liveData is not None:
                        streamInfoList = liveData['data'][0]['gameStreamInfoList']
                        for streamInfo in streamInfoList:
                            live_url_info = {}
                            sCdnType = streamInfo['sCdnType']
                            live_url_info['stream_name'] = streamInfo['sStreamName']
                            live_url_info['base_url'] = streamInfo['sHlsUrl']
                            live_url_info['hls_url'] = streamInfo['sHlsUrl'] + '/' + streamInfo['sStreamName'] + '.' + streamInfo['sHlsUrlSuffix']
                            sHlsAntiCode = streamInfo['sHlsAntiCode']
                            live_url_info.update(self.decode_live_url_info(sHlsAntiCode))
                            self.live_url_infos[sCdnType] = live_url_info
            elif self.mode == 2:
                room_url = 'https://mp.huya.com/cache.php?m=Live&do=profileRoom&roomid=' + str(self.room_id)
                header = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
                }
                response = requests.get(url=room_url, headers=header, timeout=30)
                if response.status_code == 200:
                    self.clear_live_url_infos()
                    liveData = json.loads(response.text)
                    if 'data' in liveData.keys() and 'stream' in liveData['data'].keys() and 'baseSteamInfoList' in liveData['data']['stream'].keys():
                        streamInfoList = liveData['data']['stream']['baseSteamInfoList']
                        for streamInfo in streamInfoList:
                            live_url_info = {}
                            sCdnType = streamInfo['sCdnType']
                            live_url_info['stream_name'] = streamInfo['sStreamName']
                            live_url_info['base_url'] = streamInfo['sHlsUrl']
                            live_url_info['hls_url'] = streamInfo['sHlsUrl'] + '/' + streamInfo['sStreamName'] + '.' + streamInfo['sHlsUrlSuffix']
                            sHlsAntiCode = streamInfo['sHlsAntiCode']
                            live_url_info.update(self.decode_live_url_info(sHlsAntiCode))
                            self.live_url_infos[sCdnType] = live_url_info
        except:
            pass

    def get_real_url(self, ratio = None):
        urls = []
        seqid = str(int(time.time() * 1e3 + self.user_id))
        wsTime = hex(int(time.time()) + 3600).replace('0x', '')
        for live_url_info in self.live_url_infos.values():
            hash0 = hashlib.md5((seqid + '|' + live_url_info['ctype'] + '|' + live_url_info['t']).encode('utf-8')).hexdigest()
            hash1 = hashlib.md5('_'.join([live_url_info['hash_prefix'], str(self.user_id), live_url_info['stream_name'], hash0, wsTime]).encode('utf-8')).hexdigest()
            if ratio is None:
                ratio = ''
            if 'mobile' in live_url_info['ctype']:
                url = "{}?wsSecret={}&wsTime={}&uuid={}&uid={}&seqid={}&ratio={}&txyp={}&fs={}&ctype={}&ver=1&t={}".format(
                    live_url_info['hls_url'], hash1, wsTime, live_url_info['uuid'], self.user_id, seqid, ratio, live_url_info['txyp'],
                    live_url_info['fs'], live_url_info['ctype'], live_url_info['t'])
            else:
                url = "{}?wsSecret={}&wsTime={}&seqid={}&ctype={}&ver=1&txyp={}&fs={}&ratio={}&u={}&t={}&sv=2107230339".format(
                    live_url_info['hls_url'], hash1, wsTime, seqid, live_url_info['ctype'], live_url_info['txyp'], live_url_info['fs'], ratio, self.user_id, live_url_info['t'])
            urls.append(url)
        return urls


if __name__ == '__main__':
    rid = input('输入虎牙直播间号：\n')
    real_url = huya(rid, 1463993859134, 1).get_real_url()
    if real_url is not None:
        print(real_url)
    else:
        print('未开播或直播间不存在')
