# real-url-proxy-server

## 说明
通过斗鱼、虎牙及Bilibili房间号直接访问直播源的代理服务器。

## 运行
python3 real-url-proxy-server.py [-h] -p PORT -r REFRESH [-l LOG_FILE]</br>
PORT: 端口号，服务器将监听于 0.0.0.0:PORT。</br>
REFRESH: 自动刷新间隔（秒），0表示禁止自动刷新。</br>
LOG_FILE: 日志文件路径，为空则仅输出至控制台。</br>

## 访问
**斗鱼**</br>
&ensp;&ensp;8M：http://xxx.xxx.xxx.xxx:xxxx/douyu/房间号</br>
&ensp;&ensp;4M：http://xxx.xxx.xxx.xxx:xxxx/douyu/房间号/4000</br>
&ensp;&ensp;2M：http://xxx.xxx.xxx.xxx:xxxx/douyu/房间号/2000</br>

**虎牙**</br>
&ensp;&ensp;4M：http://xxx.xxx.xxx.xxx:xxxx/huya/房间号</br>
&ensp;&ensp;2M：http://xxx.xxx.xxx.xxx:xxxx/huya/房间号/2000p</br>

**Bilibili**</br>
&ensp;&ensp;http://xxx.xxx.xxx.xxx:xxxx/bilibili/房间号</br>

## 刷新
程序首次获取到实际直播源地址后会缓存下来，后续访问会使用缓存地址。在指定的时间间隔后会自动刷新实际直播源地址，或者通过访问 http://xxx.xxx.xxx.xxx:xxxx/douyu/房间号/refresh 或 http://xxx.xxx.xxx.xxx:xxxx/huya/房间号/refresh 来手动刷新。

## 其它
获取到的实际地址会以301跳转或EXTM3U形式返回，播放端得到播放地址后，后续正常播放过程中不会再次访问代理服务器，因此服务器负载和流量均很低。本人在家中将其部署于刷了Padavan的小米路由器上，并通过OTT盒子进行观看。（斗鱼，bilibili是301跳转，虎牙会一直访问代理服务器返回#EXTM3U）

## Docker 运行
```bash
# 从本地构建镜像
docker build --tag real-url-proxy-server .
docker run -d --name real-url-proxy-server --restart unless-stopped \
    -p 8888:8888 \
    -e PORT=8888 \
    -e REFRESH=7200 \
    real-url-proxy-server

# 使用 Docker Hub 镜像
docker run -d --name real-url-proxy-server --restart unless-stopped \
    -p 8888:8888 \
    -e PORT=8888 \
    -e REFRESH=7200 \
    futuretech6/real-url-proxy-server  # 目前支持 amd64, amr64
# 也可也使用 docker-compose
docker compose up -d
```

## 感谢
获取直播源地址使用的douyu.py、huya.py及bilibili.py代码来自于<a href="https://github.com/wbt5/real-url" target="_blank">Real-Url</a>项目，在此表示由衷的感谢！
