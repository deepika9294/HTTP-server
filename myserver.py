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



#link
LINK = "./htdocs/"
RESOURCES = LINK + "resources/"
SIZE = 1024

def check_version(version):
    print(version)
    if(version == "HTTP/1.1" or version == "HTTP/1.0"):
        return -1
    else:
        return "505 HTTP Version Not Supported"

def handle_put_request(client_socket, message):
    #see the encoding thing properly
    status_code = "200 Ok"
    split_message = message[0].split("\r\n")
    print("HEADERS {}".format(split_message))

    request_0 = split_message[0].split(" ")
    # print("MESSSAAAAGEE {}".format(message[1]))
    
    file_name = LINK + request_0[1][1:]
    file_data = b"" + message[1]
    # check1 = received_message = client_socket.recv(4092)
    #get length
    request_header = {}
    for i in split_message:
        t = i.split(": ")
        if(len(t) == 2):
            request_header[t[0]] = t[1]

    length = int(request_header["Content-Length"])
    content_type = request_header["Content-Type"]
    # print(request_header, length)
    # header_length = SIZE - len(message[1])
    # length = length - header_length
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
        # print("Enter {}".format(remainder))


        try:
            file_data += data
        except TypeError:
            data = data.encode()
            file_data = file_data + data
    if(len(request_0[1].split(".")) == 1):
        file_name += '.' +content_type.split("/")[1]
    r_file = open(file_name, "wb")
    r_file.write(file_data)
    r_file.close()

    response = "HTTP/1.1 " +status_code + "\r\n"
    current_time = datetime.datetime.now()
    response += ("Date: " + current_time.strftime("%A") + ", "+ current_time.strftime("%d") + " " +  current_time.strftime("%b") + " " + current_time.strftime("%Y") + " " + current_time.strftime("%X") + " GMT\n")
    response += "Accept-Ranges: bytes\r\n"
    response += "\r\n"
    client_socket.send(response.encode())






def handle_post_data(postdata):
    data = postdata.split("&")
    parameters = {}
    for param in data:
        divide = param.split("=")
        parameters[str(divide[0])] = divide[1]
    json_data = json.dumps(parameters)
    return json_data

def handle_post_request(client_socket, message):
    flag = 0
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    
    request_header = {}
    for i in split_message:
        t = i.split(": ")
        if(len(t) == 2):
            request_header[t[0]] = t[1]

    content_type = request_header["Content-Type"]
    if(content_type == "application/x-www-form-urlencoded"): 
    
        json_response = handle_post_data(message[1])
        resource_id = str(uuid.uuid4())
        file_write = RESOURCES + resource_id + ".json"
        send_file_response = LINK + request_0[1][1:]

        if(os.path.exists(file_write)):
            status_code = "200 OK"
            content_type = "text/html"
            r_file = open(file_write, 'a')
            

        elif(not(os.path.exists(file_write))):
            status_code = "201 Created"
            content_type = "text/html"
            #create file
            r_file = open(file_write, 'w')

        r_file.write(str(json_response))
        r_file.close()
        print(send_file_response)
        if(not(os.path.exists(send_file_response))):
            status_code = "404 Not Found"
            content_type = "text/html"
            flag = 1
        
        
        current_time = datetime.datetime.now()
        response = "HTTP/1.1 " +status_code + "\r\n"
        response += ("Date: " + current_time.strftime("%A") + ", "+ current_time.strftime("%d") + " " +  current_time.strftime("%b") + " " + current_time.strftime("%Y") + " " + current_time.strftime("%X") + " GMT\n")
        response += "Accept-Ranges: bytes\r\n"
        # document_length = os.path.getsize(file_name)
        # response += "Content-Length: " + str(document_length) + "\r\n"
        response += "Content-Type: " +content_type +"; charset-utf-8\r\n"
        response += "\r\n"
        client_socket.send(response.encode())
        if(os.path.exists(send_file_response)):
            if(os.path.isdir(send_file_response)):
                #send directoy details
                client_socket.send(b"<html><head></head><body>Record Saved.</br>Requested url is a directory</body></html>")
            else:
                r_file = open(send_file_response, "rb")
                client_socket.sendfile(r_file)
                r_file.close()
        else:
            send_file_response = LINK + "error.html"
            r_file = open(send_file_response, "rb")
            client_socket.sendfile(r_file)
            r_file.close()
    else: 

        status_code ="415 Unsupported Media Type"
        current_time = datetime.datetime.now()

        response = "HTTP/1.1 " +status_code + "\r\n"
        response += ("Date: " + current_time.strftime("%A") + ", "+ current_time.strftime("%d") + " " +  current_time.strftime("%b") + " " + current_time.strftime("%Y") + " " + current_time.strftime("%X") + " GMT\n")
        response += "Accept-Ranges: bytes\r\n"
        response += "\r\n"
        client_socket.send(response.encode())




def check_extention_type(temp_content_type):
    if(len(temp_content_type) == 1):
        status_code = "404 Not Found"
        content_type = -1
        #check can be a directory
    elif(temp_content_type[1] == "html"):
        content_type = "text/html"
    elif(temp_content_type[1] == "jpg" or temp_content_type[1] == "jpeg" or temp_content_type[1] == "png"):
        content_type = "image/" + temp_content_type[1]
    elif(temp_content_type[1] == "mp3"):
        content_type = "audio/mpeg"
    elif(temp_content_type[1] == "mp4"):
        content_type = "video" + temp_content_type[1]
    
    return content_type
    

def handle_get_head_request(client_socket, split_message):
    request_0 = split_message[0].split(" ")
    #default_values    ------check if need to change
    content_type = "text/html"
    status_code = "200 OK"
    #request_0[0] defines method
    #request_0[1] defines URL
    #request_0[2] defines version
    print("REQUEST {}".format(request_0))

    # check condition of bad request

    if('/' == request_0[1]):  
        #if this happen then try to find index.html
        file_name = LINK + "index.html"
        content_type = "text/html"

    else:
        file_name = LINK + request_0[1][1:]
        print("somethingelse requested: {}".format(file_name))
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


    if os.path.exists(file_name):
        status_code = "200 OK"
        r_file = open(file_name, 'rb')
        current_time = datetime.datetime.now()
        response = "HTTP/1.1 " +status_code + "\r\n"
        response += ("Date: " + current_time.strftime("%A") + ", "+ current_time.strftime("%d") + " " +  current_time.strftime("%b") + " " + current_time.strftime("%Y") + " " + current_time.strftime("%X") + " GMT\n")
        response += "Accept-Ranges: bytes\r\n"
        document_length = os.path.getsize(file_name)
        response += "Content-Length: " + str(document_length) + "\r\n"
        response += "Content-Type: " +content_type +"; charset-utf-8\r\n"
        response += "\r\n"
        if("image" in content_type or "video" in content_type or "audio" in content_type):
            file_data = b""
            b = r_file.read(1)
            while(b != b""):
                file_data += b
                b = r_file.read(1)
            # print("FILE: {}".format(file_data))
        else:
            file_data = r_file.read(document_length)

        r_file.close()
        print("Ffd {}".format(response))
        # client_socket.send(response.encode())

    else:
        status_code = "404 Not Found"
        response = "HTTP/1.1 " + status_code +"\r\n"
        error_file = LINK + "error.html"
        r_file = open(error_file, 'rb')
        document_length = os.path.getsize(error_file)
        current_time = datetime.datetime.now()
        response += ("Date: " + current_time.strftime("%A") + ", "+ current_time.strftime("%d") + " " +  current_time.strftime("%b") + " " + current_time.strftime("%Y") + " " + current_time.strftime("%X") + " GMT\n")

        response += "Content-Length: " + str(document_length) + "\r\n"
        response += "Content-Type: text/html; charset-utf-8\r\n"
        response += "\r\n"
        file_data = r_file.read(document_length)
        r_file.close()
    # print(response)
    client_socket.send(response.encode())
    if("GET" == request_0[0]):
        client_socket.send(file_data)       


def threading(client_socket):
    #decide the size
    received_message = client_socket.recv(SIZE)
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

    #note: sending split_message in get , as we dont require entity here
    if("GET" in split_message[0] or "HEAD" in split_message[0]):
        handle_get_head_request(client_socket, split_message)
    elif("POST" in split_message[0]):
        handle_post_request(client_socket, message)
    elif("PUT" in split_message[0]):
        handle_put_request(client_socket, message)
    else:
        print("something else")
    client_socket.shutdown(SHUT_WR)

def create_server(port):
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)

    try:
        server_socket.bind(("localhost",int(port)))
        server_socket.listen(5)
        while(True):
            client_socket, client_address = server_socket.accept()
            # print("clientSocket {} and client address {}".format(client_socket,client_address))

            #threadinnggg
            # threading(client_socket)
            start_new_thread(threading,(client_socket,)) 
        # server_socket.close()    #check whether hoga ya nhi
        
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
        

