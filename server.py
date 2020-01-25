import os.path
import socket

JPG = '.jpg'
ICO = '.ico'
EMPTY = '/'
REDIRECT = "/redirect"

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = '0.0.0.0'
    server_port = 8080
    server.bind((server_ip, server_port))
    server.listen(5)
    while True:
        client_socket, client_adress = server.accept()
        data = client_socket.recv(1024)
        info = split_data(data)
        if "GET" in info[0]:
            # get file name
            message = get_message(info[0])
            file_name = get_file_name(message)
            # MIGHT HAVE TO CHANGE THIS. NEED TO FIND A BETTER WAY TO EXTRACT THE CONNECTION TYPE
            connection = get_message(info[6])
            if connection != "Connection: keep-alive":
                connection = "Connection: close"
            content = get_content(file_name, connection)
            #content is a string
            if isinstance(content, str):
                client_socket.send(content.encode())
            #content is received in bytes already
            else:
                client_socket.send(content)
        print('Client disconnected')
        client_socket.close()

#this function splits the file path from the message
def get_file_name(message):
    return message.split(" ")[1]

# this function gets the message (cleans all of the unnecessary info)
def get_message(info):
    file_name = ""
    for char in info:
        if char != '[' or char != ']':
            file_name = file_name + char
    return file_name

#this function splits the data by its lines
def split_data(data):
    return data.decode().split("\r\n")

# this function gets the file name and connections type and returns its content
def get_content(file_name, connection):
    content = file_name
    # if empty put index.html instead
    if content == EMPTY:
        file_name = "index.html"
    # any other file
    elif content == REDIRECT:
        return get_redirect_message()
    content = add_files_to_path(file_name)
    # no file found
    if not os.path.isfile(content):
        return get_not_found_message()
    # jpg file
    if content.endswith(JPG):
        return get_ico_jpg_content(content, connection)
    # ico file
    elif content.endswith(ICO):
        return get_ico_jpg_content(content, connection)
    # file is not a jpeg or ico
    else:
        return get_other_file_content(content, connection)

# this adds "files/" to the path name
def add_files_to_path(file_name):
    return "files/" + file_name

# get the content of files that are not jpeg or ico (and read normally)
def get_other_file_content(content, connection):
    file_read = open(content, 'r')
    content = file_read.read()
    file_read.close()
    beg = "HTTP/1.1 200 OK"
    msg_to_send = build_message(beg, connection, content)
    return msg_to_send

# get the content of files that are jpeg or ico (and read in binary)
def get_ico_jpg_content(content, connection):
    file_binary = open(content, 'rb')
    content = file_binary.read()
    file_binary.close()
    beg = "HTTP/1.1 200 OK"
    msg_to_send = build_JPG_ICO_message(beg, connection, content)
    return msg_to_send

# construct the not found message
#NOT WORKING
def get_not_found_message():
    msg = ""
    msg += "HTTP/1.1 404 Not Found"
    msg += "\r\n"
    msg += "Connection: close"
    msg += "\r\n"
    msg += "\r\n"
    return msg

# construct the redirect message
def get_redirect_message():
    msg = ""
    msg += "HTTP/1.1 301 Moved Permanetly"
    msg += "\r\n"
    msg += "Connection: close"
    msg += "\r\n"
    msg += "Location: /result.html"
    msg += "\r\n"
    return msg

# construct the normal message to send
def build_message(beg, conn, content):
    message = ""
    message += beg
    message += "\r\n"
    message += conn
    message += "\r\n"
    message += "Content-Length: "
    message += str(len(content))
    message += "\r\n"
    message += "\r\n"
    message += str(content)
    message += "\r\n\r\n"
    return message

# construct the jpg and ico message to send
def build_JPG_ICO_message(beg, conn, content):
    message = "".encode()
    message += beg.encode()
    message += "\r\n".encode()
    message += conn.encode()
    message += "\r\n".encode()
    message += "Content-Length: ".encode()
    message += str(len(content)).encode()
    message += "\r\n".encode()
    message += "\r\n".encode()
    message += content
    message += "\r\n\r\n".encode()
    return message

if __name__ == "__main__":
    main()