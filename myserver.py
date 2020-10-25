from socket import *
from _thread import *
import time
import threading
import sys
import os
import datetime
import json
from urllib.parse import *	 # for parsing URL/URI
import uuid
import logging
import base64
import random


#link
LINK = "./htdocs/"
RESOURCES = LINK + "resources/"
SIZE = 1024
LOGGING = LINK + "data.log"
USERNAME = "deepika"
PASSWORD = "root"
logging.basicConfig(filename = LOGGING, level = logging.INFO, format = '%(asctime)s:%(filename)s:%(message)s')


def check_version(version):
    print(version)
    if(version == "HTTP/1.1" or version == "HTTP/1.0"):
        return -1
    else:
        return "505 HTTP Version Not Supported"
def get_common_response(status_code,content_type,content_length,location,set_cookie=None, cookie=None):
    current_time = datetime.datetime.now()
    response = "HTTP/1.1 " +status_code + "\r\n"
    if(set_cookie):
        response += "Set-Cookie: " + "cookieid=" +set_cookie+ "; "+"Max-Age=60\r\n"
    if(cookie):
        response += "Cookie: " + cookie +"\r\n"
    response += ("Date: " + current_time.strftime("%A") + ", "+ current_time.strftime("%d") + " " +  current_time.strftime("%b") + " " + current_time.strftime("%Y") + " " + current_time.strftime("%X") + " GMT\n")
    response += "Accept-Ranges: bytes\r\n"
    response += "Server: Deepika\r\n"
    if(content_type):
        response += "Content-Type: " + content_type + "; charset-utf-8\r\n"

    if(content_length):
        response += "Content-Length: " + content_length + "\r\n"

    if(location):
        response += "Content-Location: " + location + "\r\n"

    return response

def handle_binary_put_request(client_socket, message):
    #see the encoding thing properly
    split_message = message[0].split("\r\n")
    print("HEADERS {}".format(split_message))
    request_0 = split_message[0].split(" ")
    # print("MESSSAAAAGEE {}".format(message[1]))
    file_name = LINK + request_0[1][1:]
    file_data = b"" + message[1]
    #get length
    request_header = {}
    for i in split_message:
        t = i.split(": ")
        if(len(t) == 2):
            request_header[t[0]] = t[1]

    length = int(request_header["Content-Length"])
    content_type = request_header["Content-Type"]
    quotient = int(length // SIZE)
    remainder = length % SIZE
    #check the size issue
    for i in range(0,quotient):
        data = client_socket.recv(SIZE)
        print(data)
        try:
            file_data += data
        except TypeError:
            data = data.encode()
            file_data = file_data + data
    if(remainder != 0):
        data = client_socket.recv(SIZE)

        try:
            file_data += data
        except TypeError:
            data = data.encode()
            file_data = file_data + data

    url_path = LINK + request_0[1][1:]        
    if(os.path.isfile(url_path)):
        r_file = open(url_path, "wb")
        r_file.write(file_data)
        r_file.close()
        status_code = "200 Not Found"

    elif(os.path.isdir(url_path)):
        put_uuid = str(uuid.uuid4())
        file_name = url_path + "/"+ put_uuid + "."+ content_type.split("/")[1]
        r_file = open(file_name, "wb")
        r_file.write(file_data)
        r_file.close()
        status_code = "201 Created"
    else:
        status_code = "404 Not Found"

    content_length = None
    location = file_name
    response = get_common_response(status_code,content_type,content_length,location) 
    response += "\r\n"
    logging.info('	{}	{}  {}\n'.format(split_message[0], status_code, location))
    client_socket.send(response.encode())

def handle_delete_request(client_socket, message):
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    request_header = {}
    for i in split_message:
        t = i.split(": ")
        if(len(t) == 2):
            request_header[t[0]] = t[1]

    cookie = None
    set_cookie = None
    if("Cookie" in request_header.keys()):
        cookie = request_header["Cookie"]
    else:
        set_cookie = str(random.randint(10000,50000))
    if(len(message[1]) != 0):
        status_code = "400 Bad Request"
        file_name = LINK + "badrequest.html"
        content_type = "text/html"
        r_file = open(file_name, 'rb')
        document_length = os.path.getsize(file_name)
        location = None
        response = get_common_response(status_code,content_type,str(document_length),location)
 
        response += "\r\n"
        file_data = r_file.read(document_length)
        r_file.close()
        logging.info('	{}	{}\n'.format(split_message[0], status_code))

        client_socket.send(response.encode())
        client_socket.send(file_data)
        return


    
    # print(request_header)
    
    if("Authorization" in request_header.keys()):
        auth = request_header['Authorization']
        auth = auth.split(' ')
        auth = base64.decodebytes(auth[1].encode()).decode()
        auth = auth.split(':')
        # print("MASSS {}".format(auth))
        if(USERNAME == auth[0] and PASSWORD == auth[1]):
            delete_url = LINK  + request_0[1][1:]
            if(os.path.isfile(delete_url)):
                os.remove(delete_url)
                status_code = "200 OK"
            else :
                status_code = "404 Not Found"
            content_type = None
            content_length = None
            location = delete_url
            response = get_common_response(status_code,content_type,content_length,location,set_cookie,cookie)   
            response += "\r\n"
            logging.info('	{}	{}  {}\n'.format(split_message[0], status_code, location))
            client_socket.send(response.encode())
        else:
            status_code = "401 Unauthorized"
            content_type = None
            content_length = None
            location = None
            response = get_common_response(status_code,content_type,content_length,location)   
            response += "\r\n"
            logging.info('	{}	{}  {}\n'.format(split_message[0], status_code, location))
            client_socket.send(response.encode())
    else: 
        #check whether this or 403
        status_code = "401 Unauthorized"
        content_type = None
        content_length = None
        location = None
        response = get_common_response(status_code,content_type,content_length,location)   
        response += "\r\n"
        logging.info('	{}	{}  {}\n'.format(split_message[0], status_code, location))
        client_socket.send(response.encode())



def handle_put_request(client_socket, message):
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    
    request_header = {}
    for i in split_message:
        t = i.split(": ")
        if(len(t) == 2):
            request_header[t[0]] = t[1]

    content_type = request_header["Content-Type"]
    if(content_type == "application/x-www-form-urlencoded"): 
        url_path = LINK + request_0[1][1:]        
        if(os.path.isfile(url_path)):
            r_file = open(url_path, 'w')
            r_file.write(parse_urlencoded(message[1]))
            r_file.close()
            status_code = "200 Ok"
            location = url_path

        elif(os.path.isdir(url_path)):
            put_uuid = str(uuid.uuid4())
            put_path = url_path +"/" + put_uuid + ".json"
            r_file = open(put_path, 'w')
            r_file.write(parse_urlencoded(message[1]))
            r_file.close()
            status_code = "201 Created"
            location = put_path


             
        else:
            status_code = "404 Not Found"

        content_length = None
        response = get_common_response(status_code,content_type,content_length,location)
        response += "\r\n"
        logging.info('	{}	{}  {}\n'.format(split_message[0], status_code, location))

        client_socket.send(response.encode())
    elif(content_type == "text/plain"):
        url_path = LINK + request_0[1][1:]        
        if(os.path.isfile(url_path)):
            r_file = open(url_path, 'w')
            r_file.write(message[1])
            r_file.close()
            status_code = "200 Ok"
            location = url_path


        elif(os.path.isdir(url_path)):
            put_uuid = str(uuid.uuid4())
            put_path = url_path +"/" + put_uuid + ".txt"
            r_file = open(put_path, 'w')
            r_file.write(message[1])
            r_file.close()
            status_code = "201 Created"
            location = put_path

        else: 
            status_code = "404 Not Found"

        content_length = None
        response = get_common_response(status_code,content_type,content_length,location)
        response += "\r\n"
        logging.info('	{}	{}  {}\n'.format(split_message[0], status_code, location))

        client_socket.send(response.encode())
    elif(content_type == "image/png" or content_type == "image/jpg"):
        handle_binary_put_request(client_socket, message)

    

def parse_urlencoded(postdata):
    data = postdata.split("&")
    parameters = {}
    for param in data:
        divide = param.split("=")
        parameters[str(divide[0])] = divide[1]
    json_data = json.dumps(parameters)
    return json_data
#dont do that redirect post-shit
def handle_post_request(client_socket, message):
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    
    request_header = {}
    for i in split_message:
        t = i.split(": ")
        if(len(t) == 2):
            request_header[t[0]] = t[1]

    content_type = request_header["Content-Type"]
    print(content_type)
    if(content_type == "application/x-www-form-urlencoded"): 
    
        json_response = parse_urlencoded(message[1])
        resource_id = str(uuid.uuid4())
        file_write = RESOURCES + resource_id + ".json"
        send_file_response = LINK + request_0[1][1:]

        if(os.path.exists(file_write)):
            status_code = "200 OK"

        elif(not(os.path.exists(file_write))):
            status_code = "201 Created"
            #create file

        content_type = "text/html"
        r_file = open(file_write, 'w')
        r_file.write(str(json_response))
        r_file.close()
        # print(send_file_response)

        # if(not(os.path.exists(send_file_response))):
        #     status_code = "404 Not Found"
        #     content_type = "text/html"
        
        content_length = None
        location = file_write
        response = get_common_response(status_code,content_type,content_length,location)
        response += "\r\n"
        logging.info('	{}	{}  {}\n'.format(split_message[0], status_code, location))

        client_socket.send(response.encode())
        client_socket.send(b"<html><head></head><body>Record Saved.</body></html>")

        # if(os.path.exists(send_file_response)):
        #     if(os.path.isdir(send_file_response)):
        #         client_socket.send(b"<html><head></head><body>Record Saved.</br>Requested url is a directory</body></html>")
        #     else:
        #         r_file = open(send_file_response, "rb")
        #         client_socket.sendfile(r_file)
        #         r_file.close()
        # else:
        #     send_file_response = LINK + "error.html"
        #     r_file = open(send_file_response, "rb")
        #     client_socket.sendfile(r_file)
        #     r_file.close()
    # elif("multipart/form-data" in content_type):
    #     print(message)
    #     print("-------------")
    #     print(message[1])
    #     post_url = RESOURCES + str(uuid.uuid4()) +".txt"
    #     request_url = LINK + request_0[1][1:]
    #     if(os.path.exists(request_url)):
    #         r_file = open(post_url, "w")
    #         for i in range(1,len(message)):
    #             r_file.write(message[i])
    #         r_file.close()
    #         status_code = "200 Ok"
    #     else:
    #         status_code = "404 Not Found"

    #     content_type = "multipart/form-data"
    #     content_length = None
    #     location = None
    #     response = get_common_response(status_code,content_type,content_length,location)

    #     response += "\r\n"
    #     client_socket.send(response.encode())

    else: 

        status_code ="415 Unsupported Media Type"
        print(message[1])
        print(content_type)
        content_length = None
        location = None
        response = get_common_response(status_code,content_type,content_length,location)

        response += "\r\n"
        logging.info('	{}	{}\n'.format(split_message[0], status_code))

        client_socket.send(response.encode())
    
#handle directory case
def handle_get_head_request(client_socket, message):
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    # is_cookie = False
    cookie = None
    set_cookie = None
    request_header = {}
    for i in split_message:
        t = i.split(": ")
        if(len(t) == 2):
            request_header[t[0]] = t[1]
    print(request_header)
    #default_values    ------check if need to change
    if("Cookie" in request_header):
        cookie = request_header["Cookie"]
    else:
        set_cookie = str(random.randint(10000,50000))

        
    content_type = "text/html"
    status_code = "202 Accepted"
    location = None
    '''request_0[0] defines method
    request_0[1] defines URL
    request_0[2] defines version
    print("REQUEST {}".format(request_0))'''
    # print(message)
    # print(len(message[1]))
    # check condition of bad request and version 
    if(len(message[1]) != 0):
        status_code = "400 Bad Request"
        file_name = LINK + "badrequest.html"
        content_type = "text/html"
        r_file = open(file_name, 'rb')
        document_length = os.path.getsize(file_name)
        location = None
        response = get_common_response(status_code,content_type,str(document_length),location)
 
        response += "\r\n"
        file_data = r_file.read(document_length)
        r_file.close()
        logging.info('	{}	{}\n'.format(split_message[0], status_code))
        client_socket.send(response.encode())
        if("GET" == request_0[0]):
            client_socket.send(file_data)
        return


    if('/' == request_0[1]):  
        #if this happen then try to find index.html
        file_name = LINK + "index.html"
        content_type = "text/html"

    else:
        file_name = LINK + request_0[1][1:]
        # print("somethingelse requested: {}".format(file_name))
        #check for type of file:
        temp_content_type = request_0[1].split(".")
        if(len(temp_content_type) == 1):
            status_code = "404 Not Found"
            #check can be a directory
        elif(temp_content_type[1] == "html"):
            content_type = "text/html"
        elif(temp_content_type[1] == "jpg" or temp_content_type[1] == "jpeg" or temp_content_type[1] == "png"):
            content_type = "image/" + temp_content_type[1]
        elif(temp_content_type[1] == "mp3"):
            content_type = "audio/mpeg"
        elif(temp_content_type[1] == "mp4"):
            content_type = "video" + temp_content_type[1]


    if os.path.isfile(file_name):
        status_code = "200 OK"
        r_file = open(file_name, 'rb')
        document_length = os.path.getsize(file_name)
        content_length = str(document_length)
        response = get_common_response(status_code,content_type,content_length,location,set_cookie,cookie)
        response += "\r\n"
        print(response)
        if("image" in content_type or "video" in content_type or "audio" in content_type):
            file_data = b""
            b = r_file.read(1)
            while(b != b""):
                file_data += b
                b = r_file.read(1)
        else:
            file_data = r_file.read(document_length)

        r_file.close()

    else:
        status_code = "404 Not Found"
        file_name = LINK + "error.html"
        r_file = open(file_name, 'rb')
        document_length = os.path.getsize(file_name)
        content_length = str(document_length)
        content_type = "text/html"
        response = get_common_response(status_code,content_type,content_length,location)
        response += "\r\n"
        file_data = r_file.read(document_length)
        r_file.close()
    # print(response)
    client_socket.send(response.encode())
    logging.info('	{}	{}\n'.format(split_message[0], status_code))

    if("GET" == request_0[0]):
        #resolve the broken pipe issue
        client_socket.send(file_data)       


def threading(client_socket,client_address):
    # while(True):
    #decide the size
    received_message = client_socket.recv(SIZE)
    w = open(LOGGING, "a")
    # print("REC {}".format(received_message))  
    try:
        received_message = received_message.decode('utf-8')
        message = received_message.split("\r\n\r\n")

        # print("STUDY {}".format(received_message))
    except UnicodeDecodeError:
        
        message = received_message.split(b"\r\n\r\n")
        # print("MESA000 {}".format(message[0]))
        message[0] = message[0].decode(errors = 'ignore')
        # print("MESA000 {}".format(message[0]))

        print("ERROR")
    split_message = message[0].split("\r\n")
    # print("MESA000 {}".format(message))
    # log.write(client_address)
    # log.write(message[0])
    w.close()


    #note: sending split_message in get , as we dont require entity here
    # handle directory here
    if("GET" in split_message[0] or "HEAD" in split_message[0]):
        handle_get_head_request(client_socket, message)
    elif("POST" in split_message[0]):
        handle_post_request(client_socket, message)
    elif("PUT" in split_message[0]):
        handle_put_request(client_socket, message)
    elif("DELETE" in split_message[0]):
        handle_delete_request(client_socket, message)
    else:
        print("something else")
    client_socket.shutdown(SHUT_WR)
    # client_socket.close()


def create_server(port):
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)

    try:
        server_socket.bind(("localhost",int(port)))
        server_socket.listen(5)
        while(True):
            client_socket, client_address = server_socket.accept()
            # print("clientSocket {} and client address {}".format(client_socket,client_address))

            start_new_thread(threading,(client_socket,client_address,)) 
        server_socket.close()    #check whether hoga ya nhi
        
    except KeyboardInterrupt:
        print("Closing....")
    except Exception as exc :
         print("ERROR")
         print(exc) 
    
    server_socket.close()



if __name__ == "__main__":
    print("Server started")
    if(len(sys.argv) < 2): 
        port = 9000
    else:
        port = sys.argv[1]
    create_server(port)
        

