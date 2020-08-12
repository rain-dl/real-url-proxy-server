# real-url-proxy-server

## 说明
通过斗鱼、虎牙平台房间号直接访问直播源的代理服务器。

## 运行
python3 real-url-proxy-server.py [-h] -p PORT</br>
PORT: 端口号，服务器将监听于 0.0.0.0:PORT.</br>

## 访问
**斗鱼**</br>
&ensp;&ensp;8M：http://xxx.xxx.xxx.xxx:xxxx/douyu/房间号</br>
&ensp;&ensp;4M：http://xxx.xxx.xxx.xxx:xxxx/douyu/房间号/4000</br>
&ensp;&ensp;2M：http://xxx.xxx.xxx.xxx:xxxx/douyu/房间号/2000</br>

**虎牙**</br>
&ensp;&ensp;4M：http://xxx.xxx.xxx.xxx:xxxx/huya/房间号</br>
&ensp;&ensp;2M：http://xxx.xxx.xxx.xxx:xxxx/huya/房间号/2000p</br>

## 刷新
程序首次获取到实际直播源地址后会缓存下来，后续访问不会再次获取。一旦直播源地址失效，可通过访问 http://xxx.xxx.xxx.xxx:xxxx/douyu/房间号/refresh 或 http://xxx.xxx.xxx.xxx:xxxx/huya/房间号/refresh 强制后台进行地址刷新。

## 其它
获取到的实际地址会以301跳转或EXTM3U形式返回，播放端得到播放地址后，后续正常播放过程中不会再次访问代理服务器，因此服务器负载和流量均很低。本人在家中将其部署于刷了Padavan的小米路由器上，并通过OTT盒子进行观看。

## 感谢
获取直播源地址使用的douyu.py及huya.py代码来自于<a href="https://github.com/wbt5/real-url" target="_blank">Real-Url</a>项目，在此表示由衷的感谢！
