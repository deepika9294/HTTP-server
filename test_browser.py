import webbrowser, os, sys
from socket import *
from config import *
# import threading
# from _thread import *
import time
from threading import Thread


def test(url):
    webbrowser.get('firefox').open_new_tab(url)


if __name__ == "__main__":
    root = LINK
    port = sys.argv[1]
    host = '127.0.0.1'
    try:
        c = socket(AF_INET, SOCK_STREAM)
        c.connect((host,port))
        print("Client connected")
    except:
        c.close()

    base_url = "http://" + 	host + ":" + port 
    # test(base_url)


    # testing get methods with already created website

    url = base_url + "/public/images.html"
    Thread(target = test, args=(url,)).start()
    url = base_url + "/public/form.html"
    Thread(target = test, args=(url,)).start()

    url = base_url + "/public/form1.html"
    Thread(target = test, args=(url,)).start()

    url = base_url + "/public/video.html"
    Thread(target = test, args=(url,)).start()
    url = base_url + "/public/ipsum.html"
    Thread(target = test, args=(url,)).start()
    url = base_url + "/public/no-file.html"
    Thread(target = test, args=(url,)).start()
    url = base_url + "/public/audio.html"
    Thread(target = test, args=(url,)).start()

    url = base_url
    Thread(target = test, args=(url,)).start()


   
