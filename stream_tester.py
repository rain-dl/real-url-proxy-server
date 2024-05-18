import os
import platform
import subprocess
import json
import argparse
import queue
import threading

def ffprobe(media_path):
    if os.path.isfile(media_path) or media_path.find('://') > 0:
        cmd = 'ffprobe -v quiet -show_streams -of json ' + media_path
        if platform.system() == 'Windows':
            cmd = cmd.split(' ')
        else:
            cmd = [cmd]

        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            out, err = p.communicate(timeout=10)
            return json.loads(out)
        except:
            p.kill()
            return None

    else:
        raise IOError('No such media file or not supported: ' + media_path)

lock = threading.Lock()

def prober(urls, dump_stream_info):
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
        except:
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stream tester.')
    parser.add_argument('-u', '--url', type=str, nargs='?', help='The stream url to test.')
    parser.add_argument('-f', '--url_file', type=str, nargs='?', help='The file contains stream urls to test.')
    parser.add_argument('-t', '--thread', type=int, default=4, help='The parallel threads.')
    parser.add_argument('-d', '--dump', default=False, action='store_true', help='Dump stream info.')
    args = parser.parse_args()

    if args.url is None and args.url_file is None:
        parser.print_usage()
        exit(-1)

    urls = queue.Queue()
    if args.url is not None:
        urls.put(args.url)
    else:
        try:
            url_file = open(args.url_file, 'r')
            lines = url_file.readlines()
            url_file.close()
            for line in lines:
                line = line.rstrip()
                urls.put(line)
        except:
            print("Failed to open url file.")
            exit(-2)

    for i in range(args.thread):
        t = threading.Thread(target=prober, args=[urls, args.dump])
        t.start()
