from socket import *
from _thread import *
import time
import threading
import sys
import os
import datetime
import json
from urllib.parse import *	 # for parsing URL/URI


#-----------------------------------------------------------------------------------------------------------------------
    #web pages are encoded in utf-8
#-----------------------------------------------------------------------------------------------------------------------

#link
LINK = "./htdocs/"

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
    request_0 = split_message[0].split(" ")
    print("MESSSAAAAGEE {}".format(message[1]))
    #message_1 is the data to be written
    file_name = LINK + "check.png"
    

    file_data = b"" + message[1]
    
    # check1 = received_message = client_socket.recv(4092)
    # check2 = received_message = client_socket.recv(4092)
    # file_data += check1
    # file_data += check2

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
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    # need changes in json data
    #definitely add this
    # if("Content-Type: application/x-www-form-urlencoded" not in split_message): 
    #     status_code = 415
        
    json_response = handle_post_data(message[1])
    file_write = LINK + "data.txt"
    if(os.path.exists(file_write)):
        status_code = "200 OK"
        content_type = "text/html"
        r_file = open(file_write, 'a')
        r_file.write(str(json_response))
        

    else:
        status_code = "201 Created"
        content_type = "text/html"
        #create file
        r_file = open(file_write, 'w')
        r_file.write(str(json_response))

    r_file.close()
    current_time = datetime.datetime.now()
    response = "HTTP/1.1 " +status_code + "\r\n"
    response += ("Date: " + current_time.strftime("%A") + ", "+ current_time.strftime("%d") + " " +  current_time.strftime("%b") + " " + current_time.strftime("%Y") + " " + current_time.strftime("%X") + " GMT\n")
    response += "Accept-Ranges: bytes\r\n"
    # document_length = os.path.getsize(file_name)
    # response += "Content-Length: " + str(document_length) + "\r\n"
    response += "Content-Type: " +content_type +"; charset-utf-8\r\n"
    response += "\r\n"
    client_socket.send(response.encode())
    saved_file = LINK + "saved.html"
    r_file = open(saved_file, "rb")
    client_socket.sendfile(r_file)
    r_file.close()

    

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
    #write a function

    
    # elif "GET" in request_0[0] or "HEAD" in request_0[0]:
    if "GET" in request_0[0] or "HEAD" in request_0[0]:

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
        print(response)
        client_socket.send(response.encode())
        if("GET" == request_0[0]):
            client_socket.send(file_data)       


def threading(client_socket):
    #decide the size
    received_message = client_socket.recv(32768)
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
    # print(message)
    split_message = message[0].split("\r\n")

    #handle in more better way
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
        

