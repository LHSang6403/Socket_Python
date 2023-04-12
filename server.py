import socket
import threading
from os import stat

HOST = "127.0.0.1"
PORT = 8080

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    SERVER.bind((HOST, PORT))
    print(f'* Running on http://{HOST}:{PORT}')
except socket.error as e:
    print(f'socket error: {e}')
    print('socket error: %s' % e)


def _start():
    SERVER.listen()

    with SERVER:
        while True:
            connect, address = SERVER.accept()
            thread = threading.Thread(target=handle, args=(connect, address))
            thread.start()


def handle(connect, address):
    with connect:
        print(f"Connected by {address}")

        while True:
            request = connect.recv(2048)
            print(f"Request by {address}")
            data = ''

            if not request:
                print(f"Close {address}")
                break

            else:
                request = request.decode()
                if get_from_header(request, 'method') == 'GET':
                    url = get_from_header(request, 'url')
                    if url == '':
                        url = 'index.html'

                    try:
                        f = open(url, 'rb')
                        f.close()
                        url_ext = '.' + url.split('.', 1)[1]
                        content_type = content_type_parser(url_ext)

                        data = read_file('200 OK', url, content_type)

                    except IOError:
                        data = read_file('404 Not Found', '404_Not_Found.html', 'text/html')

                elif get_from_header(request, 'method') == 'POST':
                    if check_post_body(request) == 1:
                        data = read_file('200 OK', 'images.html', 'text/html')

                    else:
                        data = read_file('401 Unauthorized', '401_Unauthorized.html', 'text/html')

                connect.sendall(data)


def content_type_parser(url_ext):
    if url_ext == '.html' or url_ext == '.htm':
        return 'text/html'
    if url_ext == '.txt':
        return 'text/plain'
    if url_ext == '.jpg' or url_ext == '.jpeg':
        return 'image/jpeg'
    if url_ext == '.gif':
        return 'image/gif'
    if url_ext == '.png':
        return 'image/png'
    if url_ext == '.css':
        return 'text/css'
    else:
        return 'application/octet-stream'


def get_from_header(message, key=None):
    message_array = []

    for x in message.split('\r\n'):
        if x.strip():
            message_array.append(x)
        else:
            break

    message_line = []
    for x in message_array[0].split():
        message_line.append(x)
    message_dict = dict(Method=message_line[0], Url=message_line[1][1:], Protocol=message_line[2])

    for x in message_array[1:]:
        data = x.split(':', 1)
        message_dict.update({data[0]: data[1]})

    if key is None:
        result = message_dict

    else:
        key_value = (key.lower()).title()
        result = message_dict[key_value]

    return result


def check_post_body(message):
    body_request = message.split('\r\n\r\n')[1]  # uname=admin&psw=123456&remember=on
    body_array = []
    body_dict = {}

    for x in body_request.split('&'):
        body_array.append(x)

    for x in body_array:
        data = x.split('=', 1)
        body_dict[data[0]] = data[1]

    if body_dict['uname'] == 'admin' and body_dict['psw'] == '123456':
        return 1

    else:
        return 0


def set_header(response, content_type, content_length):
    message_header = 'HTTP/1.1 ' + response + '\r\n'
    message_header += f'Content-type: {content_type}\r\n'
    message_header += f'Content-length: {content_length}\r\n'
    message_header += '\r\n'
    message_header = message_header.encode()
    return message_header


def read_file(response, Name_file, content_type):
    with open(Name_file, 'rb') as f:
        content_length = stat(Name_file).st_size
        data = set_header(response, content_type, str(content_length)) + f.read()
        return data


if __name__ == '__main__':
    _start()
