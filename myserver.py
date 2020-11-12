from socket import *
from _thread import *
import time
import threading
import sys
import os
import datetime
import json
from urllib.parse import *
import uuid
import logging
import base64
import random
from config import *
import string


isbinary = False

# logging config
logging.basicConfig(filename = LOGGING, level = logging.INFO, format = '%(asctime)s:    %(filename)s:%(message)s')

# check versions and return accordingly in the starting

def check_version(version):
    # print(version)
    if(version == "HTTP/1.1"):
        return -1
    else:
        return "505 HTTP Version Not Supported"

'''
Response function, where in different response headers cintent are being send, 
and response headers get appended in response variable
'''

def get_common_response(status_code,content_type,content_length,location,set_cookie=None, cookie=None,connection=None):
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

    if(connection):
        response +="Connection: " + connection + "\r\n"

    # if(content_encoding):
    #     response +="Content-Encoding: " + content_encoding + "\r\n"

    return response

'''
This function takes in the request headers message, and convert it into a dictionary,
having {header:header-value} key-value pair
'''
def get_headers(split_message):
    request_header = {}
    for i in split_message:
        t = i.split(": ")
        if(len(t) == 2):
            request_header[t[0]] = t[1]
    return request_header

'''
This functions handle Put request , which is off the the binary form, datas like image video etc.
Here first the content-length is checked, and accordingly, server keeps on receiving data from client.
Checks whether the file exist or not:
    If file exist: rewrite it sending 200 status code
    If not exist check whether requested url is directory or not, 
        if directory, then create a file  with random filename, and write the content, send status code 200
    Else not found
'''

def handle_binary_put_request(client_socket, message):
    #see the encoding thing properly
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
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
    length = length - len(message[1])
    quotient = int(length // SIZE)
    remainder = length % SIZE
    #check the size issue
    for i in range(0,quotient):
        data = client_socket.recv(SIZE)
        try:
            file_data += data
        except TypeError:
            data = data.encode()
            file_data = file_data + data
    if(remainder != 0):
        data = client_socket.recv(remainder)

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
        status_code = "200 Ok"

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
    # print(response)
    logging.info('	{}	{}  \n'.format(split_message[0], "\n" + response))
    client_socket.send(response.encode())

'''
---> need to give full url path after /htdocs 
DELETE METHOD
Check for body, if present than bad request, else check for authorisation.
If not authorised then send unauthorised status code:

If Authorsised check for the file existance and accordingly delete or send not found

'''

def handle_delete_request(client_socket, message):
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    
    request_header = get_headers(split_message)
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
        logging.info('	{}	{}\n'.format(split_message[0], "\n"+response))

        client_socket.send(response.encode())

        client_socket.send(file_data)
        return

    
    if("Authorization" in request_header.keys()):
        auth = request_header['Authorization']
        auth = auth.split(' ')
        auth = base64.decodebytes(auth[1].encode()).decode()
        auth = auth.split(':')
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
            logging.info('	{}	{}  \n'.format(split_message[0], "\n" + response))
            client_socket.send(response.encode())
        else:
            status_code = "401 Unauthorized"
            content_type = None
            content_length = None
            location = None
            response = get_common_response(status_code,content_type,content_length,location)   
            response += "\r\n"
            logging.info('	{}	{}  \n'.format(split_message[0], "\n"+response))
            client_socket.send(response.encode())
    else: 
        #check whether this or 403
        status_code = "401 Unauthorized"
        content_type = None
        content_length = None
        location = None
        response = get_common_response(status_code,content_type,content_length,location)   
        response += "\r\n"
        logging.info('	{}	{}  \n'.format(split_message[0], "\n" + response))
        client_socket.send(response.encode())



'''
PUT REQUESTS

'''

def handle_put_request(client_socket, message):
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    cookie = None
    set_cookie = None

    request_header = get_headers(split_message)

    if("Cookie" in request_header):
        cookie = request_header["Cookie"]
    else:
        set_cookie = str(random.randint(10000,50000))

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
        response = get_common_response(status_code,content_type,content_length,location,set_cookie ,cookie)
        response += "\r\n"
        logging.info('	{}	{}  \n'.format(split_message[0], "\n"+response))

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
            location =None

        content_length = None
        response = get_common_response(status_code,content_type,content_length,location,set_cookie,cookie)
        response += "\r\n"
        logging.info('	{}	{}  \n'.format(split_message[0], "\n"+response))

        client_socket.send(response.encode())
    elif(content_type == "image/png" or content_type == "image/jpg" or content_type == "image/jpeg"):
        handle_binary_put_request(client_socket, message)

    else:
        status_code ="415 Unsupported Media Type"
        content_length = None
        content_type = None
        location= None
        response = get_common_response(status_code,content_type,content_length,location)
        response += "\r\n"
        # logging.info('	{}	{}  {}\n'.format(split_message[0], status_code))
        logging.info('	{}	{}  \n'.format(split_message[0], "\n" + response))

        client_socket.send(response.encode())

'''
Parsing url_encoded data
Different keys are separated by &
converting it into json dump
'''

def parse_urlencoded(postdata):
    data = postdata.split("&")
    parameters = {}
    for param in data:
        divide = param.split("=")
        if(len(divide) == 2):
            parameters[str(divide[0])] = divide[1]
        else:
            parameters["null"] = "null"
    json_data = json.dumps(parameters)
    return json_data


'''
parsing multipart data for post requests
if binary data then decode with "ISO-859-1"
'''

def parse_multipart(message):
    entity_data = ""
    isbinary = False
    for i in range(1,len(message)):
        try:
            entity_data += message[i]
        except:
            # pass
            message[i] = message[i].decode("ISO-8859-1")
            entity_data += message[i]
            isbinary = True
    
    
    data = []
    split_char = entity_data.split(':')[0]
    new_message = entity_data.split(split_char + ':' )
    new_message.pop(0)
    
    for i in range(0,len(new_message)):
        new_message[i] = new_message[i].lstrip(' name=')
    if_file_exist = 0
    count = 0
    for i in new_message:
        if 'filename' in i:
            if_file_exist = 1
            filedata = i
            # print (i)
            if('png' in i):
                content_type = "Content-Type: image/png"
            elif('jpg' in i):
                content_type = "Content-Type: image/jpg"
            elif('jpeg' in i):
                content_type = "Content-Type: image/jpeg"
            elif('gif' in i):
                content_type = "Content-Type: image/gif"
            else:
                content_type =""
            break
        data.append(i)
        count += 1


    #if file exist write data into file:
    if(if_file_exist == 1):
        filename = filedata.split("filename=")
        if(len(filename) >= 2):
            fname = filename[1].split("\r\n")[0].strip('"')
            # error handling required
            if(isbinary):
                temp = filename[1].split("\r\n")
                fdata = ""
                # print("TEAMP {} {}".format(temp,len(temp)))
                for i in range(1,len(temp)):
                    fdata += temp[i]
                    if(i == 1):
                        fdata += "\r\n"
                fdata = fdata[len(content_type):]
            else:
                fdata = filename[1].split("\r\n")[1]

            # remove_string = "Content-Type" + 
            # if file already exit.. appending random string to it, might change to uuid, anyways need to append the file
            if(os.path.isfile(RESOURCES + fname)):
                letters = string.ascii_lowercase
                result_str = ''.join(random.choice(letters) for i in range(5))
                fname =  result_str+fname
            fname = RESOURCES+ fname
            if(isbinary):
                fwrite = open(fname, "wb")
                fwrite.write(fdata.encode("ISO-8859-1"))
                fwrite.close()
            else:
                fwrite = open(fname,"w")
                fwrite.write(fdata)
                fwrite.close()
        else: 
            pass
        data.append(new_message[count].split(' filename=')[0] + "filename=" + fname)
    return data

'''

POST REQUEST 
Get the request headers , check for cookies
And Check for content-type, and accordingly perform the required function
Method which are not implemented are returned with status code 415

'''

def handle_post_request(client_socket, message):
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    # print("WOW {}".format(message))
    cookie = None
    set_cookie = None
    request_header = get_headers(split_message)

    if("Cookie" in request_header):
        cookie = request_header["Cookie"]
    else:
        set_cookie = str(random.randint(10000,50000))

   

    if("Connection" in request_header):
        connection = request_header["Connection"]
    else:
        connection = None

    content_type = request_header["Content-Type"]
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
        
        content_length = None
        location = file_write
        response = get_common_response(status_code,content_type,content_length,location,set_cookie,cookie,connection)
        response += "\r\n"
        logging.info('	{}	{}  \n'.format(split_message[0], "\n" + response))

        client_socket.send(response.encode())
        client_socket.send(b"<html><head></head><body>Record Saved.</body></html>")

        
    elif("multipart/form-data" in content_type):
        if("Content-Length" in request_header.keys()):
            content_length = request_header["Content-Length"]
        else:
            pass
        data = parse_multipart(message)

        # assuming even if 404 not found, still able to dump data
        # writing the data into the file

        post_url = RESOURCES + str(uuid.uuid4()) +".txt"
        request_url = LINK + request_0[1][1:]
        # dont check here for file exist
        # if(os.path.exists(request_url)):
        r_file = open(post_url, "w")
        for i in range(0,len(data)):
            r_file.write(data[i])
        r_file.close()
        status_code = "201 Created"
        # else:
        #     status_code = "404 Not Found"

        content_type = "multipart/form-data"
        content_length = content_length
        location = post_url
        response = get_common_response(status_code,content_type,content_length,location,set_cookie,cookie)

        response += "\r\n"
        logging.info('	{}	{}  \n'.format(split_message[0], "\n" + response))

        client_socket.send(response.encode())
        # print(response)
        client_socket.send(b"<html><head></head><body>Record Saved.</body></html>")


    else: 

        status_code ="415 Unsupported Media Type"
        content_length = None
        location = None
        response = get_common_response(status_code,content_type,content_length,location)
        response += "\r\n"

        logging.info('	{}	{}\n'.format(split_message[0], "\n"+ response))
        client_socket.send(response.encode())
    



'''
Handles get as well as head request
Here messages splited into headers and requests data
Cookies are checked if already set or not
Check if the entity body is also sent or not, if sent then it is a bad request
Also check the version request
Also check whether the requested url exist or not:
    if exist: check whether have file permision or not
    else return not found web page
Checks the file type of requested document
Check whether head or get request, and accordingly send the body

'''
def handle_get_head_request(client_socket, message):
    # print("GET {}".format(message))
    split_message = message[0].split("\r\n")
    request_0 = split_message[0].split(" ")
    # is_cookie = False
    cookie = None
    set_cookie = None

    request_header = get_headers(split_message)
    if("Cookie" in request_header):
        cookie = request_header["Cookie"]
    else:
        set_cookie = str(random.randint(10000,50000))

    if("Connection" in request_header):
        connection = request_header["Connection"]
    else:
        connection = None
       
    # default values
    content_type = "text/html"
    status_code = "202 Accepted"
    location = None

    '''request_0[0] defines method
    request_0[1] defines URL
    request_0[2] defines version
    print("REQUEST {}".format(request_0))'''

    # check condition of bad request 


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
        logging.info('	{}	{}\n'.format(split_message[0], "\n"+ response))
        client_socket.send(response.encode())
        if("GET" == request_0[0]):
            client_socket.send(file_data)
        return


     #if this happen then try to find index.html

    if('/' == request_0[1]):  
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
        # Checking the permission, wheter file ahve access to read or write

        if (os.access(file_name, os.W_OK) and os.access(file_name, os.R_OK)):
            status_code = "200 OK"
            r_file = open(file_name, 'rb')
            document_length = os.path.getsize(file_name)
            content_length = str(document_length)
            response = get_common_response(status_code,content_type,content_length,location,set_cookie,cookie,connection)
            response += "\r\n"
            # print(response)
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
            status_code = "403 Forbidden"
            response = get_common_response(status_code,content_type,None,location,set_cookie,cookie)
            response += "\r\n"
            file_data = b"<html><head></head><body>Forbidden.</body></html>"

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
    logging.info('	{}	{}\n'.format(split_message[0], "\n"+ response))

    if("GET" == request_0[0]):
        #resolve the broken pipe issue
        client_socket.send(file_data)       

'''
Threaded function for accepting different request from different clients
Here following functions are implemented:
    1. Decoding of the received message is done according to utf-8
    2. If decoding undergoes any error, than ignore errors in excet block
    3. Here split_message variable contains headers which are requested
    4. With the help of header, appropriate function is called to send in the response
    5. Also checks if version is supported or not
'''

def threading(client_socket,client_address):
    received_message = client_socket.recv(SIZE)
    w = open(LOGGING, "a")
    # print("------------------------------------------------------- {}".format(SIZE))
    # print("REC {}".format(received_message))  
    # print("---------------------------------------------------------------------")
    try:
        received_message = received_message.decode('utf-8')
        message = received_message.split("\r\n\r\n")

    except UnicodeDecodeError:
        
        message = received_message.split(b"\r\n\r\n")
        message[0] = message[0].decode(errors = 'ignore')
        isbinary = True

    split_message = message[0].split("\r\n")
    w.close()

    version = split_message[0].split(" ")[2]
    if(check_version(version) != -1):
        print("version not supported")
        status_code = check_version(request_0[0])
        file_name = LINK + "version.html"
        content_type = "text/html"
        r_file = open(file_name, 'rb')
        content_length = str(os.path.getsize(file_name))
        location = None
        response = get_common_response(status_code,content_type,content_length)
        response += "\r\n"
        file_data = r_file.read(document_length)
        r_file.close()
        logging.info('	{}	{}\n'.format(split_message[0], "\n"+ response))
        client_socket.send(response.encode())
        if("GET" == request_0[0]):
            client_socket.send(file_data)
        


    elif("GET" in split_message[0] or "HEAD" in split_message[0]):
        handle_get_head_request(client_socket, message)
    elif("POST" in split_message[0]):
        handle_post_request(client_socket, message)
    elif("PUT" in split_message[0]):
        handle_put_request(client_socket, message)
    elif("DELETE" in split_message[0]):
        handle_delete_request(client_socket, message)
    else:
        print("This Request is not handled")
    client_socket.shutdown(SHUT_WR)
    # client_socket.close()

'''
Server is setup with multithreading
If ctrl-C is pressed, KeyboardInterrupt is excepted and program is terminated
'''

def create_server(port):
    server_socket = socket(AF_INET, SOCK_STREAM)

    #used to avoid getting error for "port already used"
    server_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)       

    try:
        server_socket.bind(("localhost",int(port)))
        print("Server started on port {}".format(port))

        server_socket.listen(MAXREQUEST)
        while(True):
            client_socket, client_address = server_socket.accept()
            # print("clientSocket {} and client address {}".format(client_socket,client_address))

            start_new_thread(threading,(client_socket,client_address,)) 
        server_socket.close()    
        
    except KeyboardInterrupt:
        print("Server Closing....")
    except Exception as exc :
         print("ERROR Exception")
         print(exc) 
    
    server_socket.close()


'''
Driver program
'''
if __name__ == "__main__":
    if(len(sys.argv) < 2): 
        port = 9000
    else:
        port = sys.argv[1]

    # Server is created and binded with the provided port
    create_server(port)
        

