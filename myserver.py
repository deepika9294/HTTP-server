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

def handle_request(client_socket, received_message):
    try:
        received_message = received_message.decode('utf-8')
    except UnicodeDecodeError:
        print("ERROR")
    split_message = received_message.split("\r\n")
    if "GET" in split_message[0]:
        print("ENTER GET")
        if("index.html" in split_message[0] or "GET / HTTP/" in split_message[0]):
        # if("GET / HTTP/" in split_message[0]):

            print("ENTER /")

            requested_document = LINK + "index.html"
            if os.path.exists(requested_document):
                r_file = open(requested_document, 'r')
                current_time = datetime.datetime.now()
                response = "HTTP/1.1 200 OK\r\n"
                response += ("Date: " + current_time.strftime("%A") + ", "+ current_time.strftime("%d") + " " +  current_time.strftime("%b") + " " + current_time.strftime("%Y") + " " + current_time.strftime("%X") + " GMT\n")
                response += "Accept-Ranges: bytes\r\n"
                document_length = os.path.getsize(requested_document)
                response += "Content-Length: " + str(document_length) + "\r\n"
                response += "Content-Type: text/html; charset-utf-8\r\n"
                response += "\r\n"
                response += r_file.read()
                r_file.close()
                client_socket.send(response.encode())

            else:
                response = "HTTP/1.1 400 Bad Request\n"
                response += "Content-Type: text/html; charset-utf-8\r\n"
                error_file = LINK + "error.html"
                r_file = open(error_file, 'r')
                # size_of_error_file = os.path.getsize()
                response += r_file.read()
                r_file.close()
                client_socket.send(response.encode())

                


    #sending response..... shoud be in other func
    
    print("DECODED_MESSAGE ::: {}".format(received_message))
    print("SPLIT_MESSAGE ::: {}".format(split_message))



def threading(client_socket):
    #decide the size
    received_message = client_socket.recv(2046)  
    handle_request(client_socket, received_message)
    
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
        

