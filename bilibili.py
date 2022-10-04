# 获取哔哩哔哩直播的真实流媒体地址，默认获取直播间提供的最高画质
# qn=150高清
# qn=250超清
# qn=400蓝光
# qn=10000原画
# 获取方法参考：https://blog.csdn.net/zy1281539626/article/details/112451021

import requests


class BiliBili:

    def __init__(self, rid):
        self.rid = rid

    def get_real_url(self):
        # 先获取直播状态和真实房间号
        r_url = 'https://api.live.bilibili.com/room/v1/Room/room_init?id={}'.format(self.rid)
        with requests.Session() as s:
            res = s.get(r_url, timeout=30).json()
        code = res['code']
        if code == 0:
            live_status = res['data']['live_status']
            if live_status == 1:
                room_id = res['data']['room_id']

                def u(pf):
                    f_url = 'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo'
                    params = {
                        'room_id': room_id,
                        'no_playurl': 0,
                        'mask': 0,
                        'qn': 10000,
                        'platform': pf,
                        'protocol': 1,  # http_hls: 1
                        'format': 2,    # fmp4: 2
                        'codec': '0,1'  # avc: 0, hevc: 1
                    }
                    resp = s.get(f_url, params=params, timeout=30).json()
                    try:
                        codec = resp['data']['playurl_info']['playurl']['stream'][0]['format'][0]['codec'][0]
                        real_url = codec['url_info'][0]['host'] + codec['base_url'] + codec['url_info'][0]['extra']
                        return real_url
                    except KeyError or IndexError:
                        raise Exception('获取失败')

                return {
                    'hls_url': u('web'),
                }

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
    print(get_real_url(r))
