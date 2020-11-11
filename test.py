import webbrowser, os, sys
from socket import *
from config import *
import time
from threading import Thread
import requests


def get(url):
    x = requests.get(url)
    print("GET {}".format(x))

def delete(url):
    x = requests.delete(url, auth = ('deepika', 'root'))
    print("DELETE {}".format(x))
    

def delete_unauth(url):
    x = requests.delete(url)
    print("DELETE UNAUTHORISED {}".format(x))

# def post_multipart(url,file):
#     time.sleep(1)
#     x = requests.post(url, files=file)
#     print("POST Multipart: {}".format(x.content))

def post(url, obj):
    time.sleep(1)
    x = requests.post(url, data=obj)
    resource = x.headers["Content-Location"]
    print("POST {} Content-Location: {}".format(x,resource))

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



    '''
    POST REQUESTS
    '''
    url = base_url + "/public"
    obj = {'key1': 'value1', 'key2': 'value2'}
    Thread(target = post, args=(url,obj,)).start()

    # url = base_url
    # files = {'file1.png': open('./testing_files/favicon-16x16.png', 'rb')}
    # Thread(target = post_multipart, args=(url,files,)).start()


    # geting get methods with already created website
    '''GET REQUESTS'''

    urls = [
        base_url + "/public/images.html",
        base_url + "/public/form.html",
        base_url + "/public/form1.html",
        base_url + "/public/video.html",
        base_url + "/public/ipsum.html",
        base_url + "/public/no-file.html",
        base_url + "/public/audio.html",
        base_url,

    ]
    for url in urls:
        Thread(target = get, args=(url,)).start()

    

    '''
    DELETE REQUESTS

    Whenever we post any data, data is dumped into resources folder, so in this piece of code,
    first files are fetched from resources directory and they are deleted accordingly
    '''
    files_name = os.listdir("./htdocs/resources")

    # deleting with no authorisation:
    if(files_name):
        url = base_url + "/resources/" + files_name[0]
        Thread(target = delete_unauth, args=(url,)).start()
    
    #deleting files which are not available:
    url = base_url + "/resources/nope"
    Thread(target = delete, args=(url,)).start()

    for i in files_name:
        print(i)
        url = base_url + "/resources/" +i
        Thread(target = delete, args=(url,)).start()
    
    


   
