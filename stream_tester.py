import os
import platform
import subprocess
import json
import argparse
import queue
import threading
import re
from urllib.parse import unquote

def url_to_filename(url):
    # 先解码URL
    decoded_url = unquote(url)
    # 去除协议部分（如http://或https://）
    cleaned_url = re.sub(r'^https?://', '', decoded_url)
    # 替换非法字符为下划线
    filename = re.sub(r'[/\\?%*:|"<>]', '_', cleaned_url)
    return filename

def ffprobe(media_path):
    if os.path.isfile(media_path) or media_path.find('://') > 0:
        cmd = ['ffprobe', '-v', 'quiet', '-show_streams', '-of', 'json', media_path]
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            out, err = p.communicate(timeout=10)
            return json.loads(out)
        except:
            p.kill()
            return None
    else:
        raise IOError('No such media file or not supported: ' + media_path)

def grab_thumbnail(url, output_dir):
    cmd = ['ffmpeg', '-i', url, '-vframes', '1', '-f', 'image2', os.path.join(output_dir, url_to_filename(url)) + '.jpg', '-y']
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        p.wait(10)
        if p.poll() is None:
            p.kill()
    except:
        pass

lock = threading.Lock()

def prober(urls, dump_stream_info, thumbnail_dir):
    while not urls.empty():
        url = urls.get()
        try:
            meta = ffprobe(url)
            if (meta is not None and len(meta) > 0 and 'streams' in meta and len(meta['streams']) > 0):
                lock.acquire()
                print(url)
                if (dump_stream_info):
                    print(json.dumps(meta, indent=4))
                    print()
                lock.release()
                if (thumbnail_dir is not None):
                    grab_thumbnail(url, thumbnail_dir)
        except:
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stream tester.')
    parser.add_argument('-u', '--url', type=str, nargs='?', help='The stream url to test.')
    parser.add_argument('--start', type=int, help='The start number for wildcard in url.')
    parser.add_argument('--end', type=int, help='The end number for wildcard in url.')
    parser.add_argument('-f', '--url_file', type=str, nargs='?', help='The file contains stream urls to test.')
    parser.add_argument('-t', '--thread', type=int, default=4, help='The parallel threads.')
    parser.add_argument('--thumb_dir', type=str, nargs='?', help='The folder to save thumbnail files.')
    parser.add_argument('-d', '--dump', default=False, action='store_true', help='Dump stream info.')
    args = parser.parse_args()

    if args.url is None and args.url_file is None:
        parser.print_usage()
        exit(-1)

    urls = queue.Queue()
    if args.url is not None:
        if '%' in args.url and args.start is not None and args.end is not None:
            for i in range(args.start, args.end + 1):
                urls.put(args.url % i)
        else:
            urls.put(args.url)
    else:
        try:
            url_file = open(args.url_file, 'r', encoding='utf-8')
            lines = url_file.readlines()
            url_file.close()
            for line in lines:
                line = line.rstrip()
                urls.put(line)
        except Exception as e:
            print("Failed to open url file, error: ", e)
            exit(-2)

    for i in range(args.thread):
        t = threading.Thread(target=prober, args=[urls, args.dump, args.thumb_dir])
        t.start()
