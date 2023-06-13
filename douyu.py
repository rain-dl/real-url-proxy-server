# 获取斗鱼直播间的真实流媒体地址，默认最高画质
import hashlib
import re
import time

import requests

try:
    import quickjs
    use_quickjs = True
except ImportError:
    import execjs
    use_quickjs = False


class DouYu:
    def __init__(self, rid):
        """
        房间号通常为1~8位纯数字，浏览器地址栏中看到的房间号不一定是真实rid.
        Args:
            rid:
        """
        self.did = '10000000000000000000000000001501'

        self.s = requests.Session()
        self.res = self.s.get('https://m.douyu.com/' + str(rid), timeout=30).text
        result = re.search(r'rid":(\d{1,8}),"vipId', self.res)

        if result:
            self.rid = result.group(1)
        else:
            raise Exception('房间号错误')

    @staticmethod
    def md5(data):
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def get_pre(self):
        url = 'https://playweb.douyucdn.cn/lapi/live/hlsH5Preview/' + self.rid
        data = {
            'rid': self.rid,
            'did': self.did
        }
        t13 = str(int((time.time() * 1000)))
        auth = DouYu.md5(self.rid + t13)
        headers = {
            'rid': self.rid,
            'time': t13,
            'auth': auth
        }
        res = self.s.post(url, headers=headers, data=data, timeout=30).json()
        error = res['error']
        data = res['data']
        key = ''
        url = ''
        if data:
            rtmp_live = data['rtmp_live']
            url = data['rtmp_url'] + '/' + rtmp_live
            key = re.search(r'(\d{1,8}[0-9a-zA-Z]+)_?\d{0,4}p?(.m3u8|/playlist)', rtmp_live).group(1)
        return error, key, url

    def get_js(self):
        result = re.search(r'(function ub98484234.*)\s(var.*)', self.res).group()
        func_ub9 = re.sub(r'eval.*;}', 'strc;}', result)
        if use_quickjs:
            js_func = quickjs.Function('ub98484234', func_ub9)
            res = js_func()
        else:
            js = execjs.compile(func_ub9)
            res = js.call('ub98484234')

        v = re.search(r'v=(\d+)', res).group(1)
        t10 = str(int(time.time()))
        rb = DouYu.md5(self.rid + self.did + t10 + v)

        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace('CryptoJS.MD5(cb).toString()', '"' + rb + '"')

        if use_quickjs:
            js_func = quickjs.Function('sign', func_sign)
            params = js_func(self.rid, self.did, t10)
        else:
            js = execjs.compile(func_sign)
            params = js.call('sign', self.rid, self.did, t10)

        params += '&ver=219032101&rid={}&rate=-1'.format(self.rid)

        url = 'https://m.douyu.com/api/room/ratestream'
        res = self.s.post(url, params=params, timeout=30).json()['data']
        key = re.search(r'(\d{1,8}[0-9a-zA-Z]+)_?\d{0,4}p?(.m3u8|/playlist)', res['url']).group(1)

        return key, res['url']

    def get_pc_js(self, cdn='ws-h5', rate=0):
        """
        通过PC网页端的接口获取完整直播源。
        :param cdn: 主线路ws-h5、备用线路tct-h5
        :param rate: 1流畅；2高清；3超清；4蓝光4M；0蓝光8M或10M
        :return: JSON格式
        """
        res = self.s.get('https://www.douyu.com/' + str(self.rid), timeout=30).text
        result = re.search(r'(vdwdae325w_64we[\s\S]*function ub98484234[\s\S]*?)function', res).group(1)
        func_ub9 = re.sub(r'eval.*?;}', 'strc;}', result)
        if use_quickjs:
            js_func = quickjs.Function('ub98484234', func_ub9)
            res = js_func()
        else:
            js = execjs.compile(func_ub9)
            res = js.call('ub98484234')

        v = re.search(r'v=(\d+)', res).group(1)
        t10 = str(int(time.time()))
        rb = DouYu.md5(self.rid + self.did + t10 + v)

        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace('CryptoJS.MD5(cb).toString()', '"' + rb + '"')

        if use_quickjs:
            js_func = quickjs.Function('sign', func_sign)
            params = js_func(self.rid, self.did, t10)
        else:
            js = execjs.compile(func_sign)
            params = js.call('sign', self.rid, self.did, t10)

        params += '&cdn={}&rate={}'.format(cdn, rate)
        url = 'https://www.douyu.com/lapi/live/getH5Play/{}'.format(self.rid)
        res = self.s.post(url, params=params, timeout=30).json()['data']

        return res['rtmp_url'] + '/' + res['rtmp_live']

    def get_real_url(self):
        ret = {}
        error, key, url = self.get_pre()
        if error == 0:
            ret['900p'] = url
        elif error == 102:
            raise Exception('房间不存在')
        elif error == 104:
            raise Exception('房间未开播')
        key, url = self.get_js()
        ret['2000p'] = url
        #ret['flv'] = "http://openhls-tct.douyucdn2.cn/live/{}.flv?uuid=".format(key)
        return ret


if __name__ == '__main__':
    r = input('输入斗鱼直播间号：\n')
    s = DouYu(r)
    print(s.get_real_url())
