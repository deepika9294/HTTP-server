from socket import *
from _thread import *
import threading

def threading(client_socket):
    received_message = client_socket.recv(2046).decode()  #need to change the size
    print("bfhsb")
    print(received_message)
    split_message = received_message.split("\n")
    if(len(split_message) > 0):
        print(split_message[0])
    data = "HTTP/1.1 200 OK\r\n"
    data += "Content-Type: text/html; charset-utf-8\r\n"
    data += "\r\n"
    data += "<html><body>HI</body></html>"
    client_socket.sendall(data.encode())
    client_socket.shutdown(SHUT_WR)

def create_server():
    server_socekt = socket(AF_INET, SOCK_STREAM)
    try:
        server_socekt.bind(("localhost",9000))
        server_socekt.listen(5)
        while(True):
            client_socket, client_address = server_socekt.accept()
            # print("clientSocket {} and client address {}".format(client_socket,client_address))

            #-------------------------------------------------------------------------#

            #threadinnggg
            # threading.Thread(target=_listen, args=(app, client_connection, client_address)).start()
            start_new_thread(threading,(client_socket,)) 
            #---------------------------------------------------------------------------#
        # server_socekt.close()    #check whether hoga ya nhi

            
        
    except KeyboardInterrupt:
        print("Closing....")
    except Exception as exc :
         print("ERROR")
         print(exc) 
    
    server_socekt.close()



if __name__ == "__main__":
    print("Server started")
    create_server()
        

