# 获取哔哩哔哩直播的真实流媒体地址，默认获取直播间提供的最高画质
# qn=150高清
# qn=250超清
# qn=400蓝光
# qn=10000原画
# 获取方法参考：https://blog.csdn.net/zy1281539626/article/details/112451021

import requests
import json

class BiliBili:

    def __init__(self, rid):
        self.rid = rid

    def get_real_url(self):
        header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
        }

        # 先获取直播状态和真实房间号
        r_url = 'https://api.live.bilibili.com/room/v1/Room/room_init?id={}'.format(self.rid)
        with requests.Session() as s:
            res = s.get(r_url, headers=header, timeout=30).json()
        code = res['code']
        if code == 0:
            live_status = res['data']['live_status']
            if live_status == 1:
                room_id = res['data']['room_id']

                urls = {}
                f_url = 'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo'
                params = {
                    'room_id': room_id,
                    'no_playurl': 0,
                    'mask': 0,
                    'qn': 10000,
                    'platform': 'web',
                    'protocol': '0,1',  # http_stream: 0, http_hls: 1
                    'format': '0,1,2',  # flv: 0, ts: 1, fmp4: 2
                    'codec': '0,1'      # avc: 0, hevc: 1
                }
                resp = s.get(f_url, params=params, headers=header, timeout=30).json()
                try:
                    streams = resp['data']['playurl_info']['playurl']['stream']
                    for stream in streams:
                        protocol_name = stream['protocol_name']
                        for format in stream['format']:
                            format_name = format['format_name']
                            for codec in format['codec']:
                                codec_name = codec['codec_name']
                                for url_info in codec['url_info']:
                                    urls[protocol_name + '_' + format_name + '_' + codec_name] = url_info['host'] + codec['base_url'] + url_info['extra']

                    return {k: urls[k] for k in sorted(urls.keys())}
                except KeyError or IndexError:
                    raise Exception('获取失败')

            else:
                raise Exception('未开播')
        else:
            raise Exception('房间不存在')


def get_real_url(rid):
    try:
        bilibili = BiliBili(rid)
        return bilibili.get_real_url()
    except Exception as e:
        print('Exception：', e)
        return False


if __name__ == '__main__':
    r = input('请输入bilibili直播房间号：\n')
    print(json.dumps(get_real_url(r), indent=4))
