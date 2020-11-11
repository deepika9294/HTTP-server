import webbrowser, os, sys
from socket import *
from config import *
import time
from threading import Thread
import requests


def get(url):
    x = requests.get(url)
    print("GET: {}".format(x))

def get_bad_request(url):
    time.sleep(4)
    x = requests.get(url, data={"key1":"1"})
    print("GET BAD REQUEST: {}".format(x))

def head(url):
    x = requests.head(url)
    print("HEAD: {}".format(x))



def delete(url):
    x = requests.delete(url, auth = ('deepika', 'root'))
    print("DELETE: {}".format(x))
    
def delete_unauth(url):
    x = requests.delete(url)
    print("DELETE UNAUTHORISED: {}".format(x))


def post(url, obj):
    time.sleep(1)
    x = requests.post(url, data=obj)
    resource = x.headers["Content-Location"]
    print("POST {} Content-Location: {}".format(x,resource))

def post_multipart(url,file):
    time.sleep(1)
    x = requests.post(url, files=file)
    resource = x.headers["Content-Location"]
    print("POST Multipart: {} Content-Location: {}".format(x,resource))

def put(url,obj):
    time.sleep(3)
    x = requests.put(url, data = obj) 
    resource = x.headers["Content-Location"]
    print("PUT {} Content-Location: {}".format(x,resource))

def put_file(url,filename,path,content_type):
    time.sleep(4)
    headers = headers = {'Content-Type': content_type, 'Slug': filename}
    x = requests.put(url, data=open(path, 'rb'), headers=headers)
    resource = x.headers["Content-Location"]
    print("PUT FILE : {} Content-Location: {}".format(x,resource))




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
    # post data or urlencodedform
    url = base_url + "/public"
    obj = {'key1': 'value1', 'key2': 'value2'}
    Thread(target = post, args=(url,obj,)).start()

    #post data for file
    url = base_url
    files = {'file': ('favicon-16x16.png', open('./testing_files/favicon-16x16.png', 'rb'), 'image/png')}
    Thread(target = post_multipart, args=(url,files,)).start()

    #post data to the url, which does not exist
    url = base_url+ "/nope"
    Thread(target = post, args=(url,obj,)).start()
    

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

    url = urls[0]
    Thread(target = get_bad_request, args=(url,)).start()
    
    '''
    HEAD
    '''
    for url in urls:
        Thread(target = head, args=(url,)).start()

    '''
    PUT
    '''
    objput = {'put1': 'value1', 'put2': 'value2'}
    # already existing file
    url = base_url + "/test_put/test.txt"
    Thread(target = put, args=(url,objput,)).start()

    # file do not exist already
    url = base_url + "/resources" 
    Thread(target = put, args=(url,objput,)).start()
    
    #put with an image
    url = base_url + "/resources" 
    path = "./testing_files/favicon-16x16.png"
    filename = "favicon-16x16.png"
    content_type = "image/png"
    Thread(target = put_file, args=(url,filename,path, content_type)).start()

    # need time to run next
    time.sleep(1)

    #put with a text file
    url = base_url + "/resources" 
    path = "./testing_files/post_text.txt"
    filename = "favicon-16x16.png"
    content_type = "text/plain"
    Thread(target = put_file, args=(url,filename,path, content_type)).start()


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
        # print(i)
        url = base_url + "/resources/" +i
        Thread(target = delete, args=(url,)).start()
    
    


   
