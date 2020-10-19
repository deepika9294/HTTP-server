from socket import *
from _thread import *
import time
import threading
import sys
import os
import datetime

#-----------------------------------------------------------------------------------------------------------------------
    #web pages are encoded in utf-8
#-----------------------------------------------------------------------------------------------------------------------

#link
LINK = "./htdocs/"

def handle_get_request(client_socket, split_message):
    request_0 = split_message[0].split(" ")
    #default_values    ------check if need to change
    content_type = "text/html"
    status_code = "200 OK"
    #request_0[0] defines method
    #request_0[1] defines URL
    #request_0[2] defines version
    print("REQUEST {}".format(request_0))

    # check whether to keep or not
    if(len(request_0) < 3):
        status_code = "400 Bad Request"
        #send the response here itself and return
   
    elif "GET" in request_0[0]:
        print("ENTER GET")


        if('/' == request_0[1]):  
            #if this happen then try to find index.html
            print("ENTER /")

            requested_document = LINK + "index.html"
            content_type = "text/html"

        else:
            requested_document = LINK + request_0[1][1:]
            print("somethingelse requested: {}".format(requested_document))
            #check for type of file:
            temp_content_type = request_0[1].split(".")
            if(len(temp_content_type) == 1):
                status_code = "404 Not Found"
                requested_document = LINK + "error.html"
            elif(temp_content_type[1] == "html"):
                content_type = "text/html"
            elif(temp_content_type[1] == "jpg" or temp_content_type[1] == "jpeg" or temp_content_type[1] == "png"):
                content_type = "image/" + temp_content_type[1]
            elif(temp_content_type[1] == "mp3"):
                content_type = "audio/mpeg"
            elif(temp_content_type[1] == "mp4"):
                content_type = "video" + temp_content_type[1]



        if os.path.exists(requested_document):
            status_code = "200 OK"
            r_file = open(requested_document, 'rb')
            current_time = datetime.datetime.now()
            response = "HTTP/1.1 " +status_code + "\r\n"
            response += ("Date: " + current_time.strftime("%A") + ", "+ current_time.strftime("%d") + " " +  current_time.strftime("%b") + " " + current_time.strftime("%Y") + " " + current_time.strftime("%X") + " GMT\n")
            response += "Accept-Ranges: bytes\r\n"
            document_length = os.path.getsize(requested_document)
            response += "Content-Length: " + str(document_length) + "\r\n"
            response += "Content-Type: " +content_type +"; charset-utf-8\r\n"
            response += "\r\n"
            # response += r_file.read(document_length)
            if("image" in content_type or "video" in content_type or "audio" in content_type):
                # file_data = r_file.read(document_length)
                file_data = b""
                b = r_file.read(1)
                while(b != b""):
                    file_data += b
                    b = r_file.read(1)

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
            response += "Content-Length: " + str(document_length) + "\r\n"
            response += "Content-Type: text/html; charset-utf-8\r\n"
            response += "\r\n"
            
            # size_of_error_file = os.path.getsize()
            # response += r_file.read(document_length)
            file_data = r_file.read(document_length)

            print(response)
            r_file.close()
        client_socket.send(response.encode())
        client_socket.send(file_data)       #checkif sendfile


    # print("DECODED_MESSAGE ::: {}".format(received_message))
    # print("SPLIT_MESSAGE ::: {}".format(split_message))

                

    #check for version, otherwise send bad request

    
    



def threading(client_socket):
    #decide the size
    received_message = client_socket.recv(2046)  
    try:
        received_message = received_message.decode('utf-8')
        # print("STUDY {}".format(received_message))
    except UnicodeDecodeError:
        print("ERROR")
    split_message = received_message.split("\r\n")
    #handle in more better way
    if("GET" in split_message[0]):
        handle_get_request(client_socket, split_message)
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
        

