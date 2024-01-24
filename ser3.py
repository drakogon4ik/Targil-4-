"""
Author: Oleg Shkolnik יא9.
Description: Server that receives GET or POST request from client (site) and sends answer:
             for GET request with no parameters from user:
                sends:
                status of request (200 OK / 404 Not Found / 400 Bad Request / 302 Moved Temporarily
                                                                  / 403 Forbidden / 500 Internal Server Error),
                length of content,
                type of content,
                content.
             for GET request with parameters from user:
                finds name of the command and from this sends the answer (200 OK with number plus 1 /
                                                                                with area /
                                                                                with the photo).
             for POST request:
                sends status of request with filename that it sent, and it's length.
Date: 24/01/24
"""

import socket
import os

error = 'NaN'
HOST = '0.0.0.0'
PORT = 80
SITE_FOLDER = 'webroot'
SPARE_URL = 'index.html'
SOCKET_TIMEOUT = 2
specific_urls = ['forbidden', 'moved', 'error']
request_error = b"HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>"
types = {
    'tml': 'text/html;charset=utf-8',
    'css': 'text/css',
    '.js': 'text/javascript; charset=UTF-8',
    'txt': 'text/plain',
    'ico': 'image/x-icon',
    'gif': 'image/jpeg',
    'jpg': 'image/jpeg',
    'png': 'image/jpeg',
    'peg': 'image/jpeg'
}


def choosing_type(filename):
    """
    function for searching type of file
    :param filename: file which type we want to know
    :return: type
    """
    content_type = types[filename[-3:]]
    return content_type


def specific(filename):
    """
    function checks if we have specific url
    :param filename: specific part
    :return: true or false
    """
    return filename in specific_urls


def searching_url(filename):
    """
    function that determines what response we need to send on specific url
    :param filename: specific url
    :return: specific response
    """
    response = b''
    if filename == 'forbidden':
        response = b"HTTP/1.1 403 Forbidden\r\n\r\n<h1>403 Forbidden</h1>"
    elif filename == 'moved':
        response = b"HTTP/1.1 302 Moved Temporarily\r\nLocation: " + bytes(SPARE_URL, 'utf-8') + b"\r\n\r\n"
    elif filename == 'error':
        response = b"HTTP/1.1 500 Internal Server Error\r\n\r\n<h1>500 Internal Server Error</h1>"
    return response


def validating_get_request(request):
    """
    function validates if GET request is correct
    :param request: GET request in type of list
    :return: true if request is correct and false if not
    """

    return request[0] == "GET" and request[2] == "HTTP/1.1"


def validating_post_request(request):
    """
    function validates if GET request is correct
    :param request: GET request in type of list
    :return: true if request is correct and false if not
    """

    return request[0] == "POST" and request[2] == "HTTP/1.1"


def receive_all(sock, def_size=1024):
    """
    function make sure that we received all information
    :param sock: socket of client from which we receiv data
    :param def_size: default type of socket.recv
    :return: all data
    """
    data = b''
    while True:
        chunk = sock.recv(def_size)
        if not chunk:
            break
        data += chunk
        if len(chunk) < def_size:
            break
    return data


def serve_file(filename):
    """
    This function opens a file requested from the browser and sends its contents to the client via a socket.
    If the file is not found, a "404 Not Found" message is sent.
    param filename: path to the file
    return: send response on the get request with headers: "200 OK" or "404 not found"
    """
    try:
        with open(filename, 'rb') as file:
            content = file.read()
            content_type = choosing_type(filename)
            headers = f"Content-Type: {content_type}\nContent-Length: {len(content)}\r\n\r\n".encode()
            response = b"HTTP/1.1 200 OK\r\n" + headers + content
    except FileNotFoundError:
        with open(r'webroot\imgs\error.jpg', 'rb') as file:
            content = file.read()
            headers = f"Content-Type: {types['jpg']}\nContent-Length: {len(content)}\r\n\r\n".encode()
            response = b"HTTP/1.1 404 Not Found\r\n" + headers + content
    return response


def post_request(client_socket, url, headers):
    """
    function sends response on the post request with file's name, and it's size
    :param client_socket: socket from which function gets data
    :param url: string, which function works with
    :param headers: dictionary with all headers of the post request
    :return: "200 OK" response on the post request with file's name, and it's size
    """
    filename = getting_path(url)

    content_length = int(headers['Content-Length'])

    handle_post_request(client_socket, content_length, filename)

    response = f'HTTP/1.1 200 OK\r\n\r\nYou Sent File {filename} of size {str(content_length)}'.encode()

    return response


def step_over(request):

    """
    function gets string, checks that user wrote number, takes it and sends this number plus 1
    :param request: string function works with
    :return: "NaN" if we get error or number plus 1 if everything is ok
    """

    url_parts = request.split('?')
    last_number = 0
    if len(url_parts) > 1:

        params = url_parts[1].split('=')
        try:
            last_number += int(params[1]) + 1
            return str(last_number)
        except ValueError:
            return "NaN"
    return "NaN"


def calculating_area(request):

    """
    function gets string, checks that user wrote numbers, takes them and calculate area from them
    :param request: string function works with
    :return: "NaN" if we get error or area if everything is ok
    """

    url_parts = request.split('?')

    if len(url_parts) > 1:

        params = url_parts[1].split('&')

        height = 0
        width = 0

        for param in params:
            key, value = param.split('=')

            if key == 'height':
                height = value
            elif key == 'width':
                width = value

        try:

            area = (int(height) * int(width)) / 2
            return str(area)
        except ValueError:
            return "NaN"
    return "0"


def getting_path(url_string):
    """
    function gets string, cuts it and takes name of the file
    :param url_string: string function works with
    :return: name of the file from the string
    """
    url_parts = url_string.split('?')

    if len(url_parts) > 1:

        filename = ''

        params = url_parts[1].split('=')

        if len(params) > 1:
            filename = params[1]

        if filename is not None:
            return filename
        else:
            return "-"
    else:
        return "-"


def validating_param(url):
    """
    function checks if function has parameters from user
    :param url: string in which function searches "?" to check if it has parameters from user
    :return: true if function has parameters or false if not
    """
    return "?" in url


def definition(url):
    """
    functions checks what parameters the request has and do the command depending on it's name
    :param url: string which function works with (checks different names of commands)
    :return: result of making command
    """
    response = b''
    if 'calculate-next' in url:
        next_num = step_over(url)
        headers = f"Content-Type: {types['txt']}\nContent-Length: {len(next_num)}"
        response = f'HTTP/1.1 200 OK\r\n{headers}\r\n\r\n{next_num}'.encode()
    elif 'calculate-area' in url:
        area = calculating_area(url)
        headers = f"Content-Type: {types['txt']}\nContent-Length: {len(area)}"
        response = f'HTTP/1.1 200 OK\r\n{headers}\r\n\r\n{area}'.encode()
    elif 'image' in url:
        filename = getting_path(url)
        if filename[-3:] in types:
            response = serve_file(filename)
        else:
            headers = f"Content-Type: {types['txt']}\nContent-Length: {len(error)}"
            response = f'HTTP/1.1 404 Not Found\r\n{headers}\r\n\r\n{error}'.encode()
    return response


def handle_post_request(client_socket, content_length, filename):
    """
    function receives data from post request and saves photo which was sent
    :param client_socket: socket from which it gets data
    :param content_length: length of data of photo
    :param filename: name of the file in which we put data
    :return:
    """
    received_data = b''

    while len(received_data) < content_length:
        data = receive_all(client_socket)
        if not data:
            break
        received_data += data

    with open(filename, 'wb') as file:
        file.write(received_data)


def parse_request(request):
    """
    function cuts the request it got twice, and return type of request with path to the file in it
    :param request: all received data
    :return: type of request with path to the file in it
    """
    method, path, *_ = request.split('\r\n')[0].split()
    return method, path


def parse_headers(request):
    """
    function makes dictionary of headers
    :param request: all received data
    :return: dictionary of headers
    """
    headers = request.split('\r\n\r\n')[0].split('\r\n')[1:]
    headers_dict = {}
    for header in headers:
        key, value = header.split(': ')
        headers_dict[key] = value
    return headers_dict


def main():
    """
    This function creates a server socket that accepts requests from clients.
    When a request is received, a new socket is opened for the client.
    The server then accepts the request from the client, processes it,
    and sends a response back to the client via the created socket.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print(f"the server is running on the port {PORT}")

        while True:
            """
            Requests from the client are processed.
            The requested file is extracted from the request and 
            the path to this file is formed in accordance with the site folder.
            If the request contains an error or the file path is not specified,
            the server sends back a "400 Bad Request" message.
            """
            client_socket, addr = server_socket.accept()
            try:
                client_socket.settimeout(SOCKET_TIMEOUT)
                print(f"Connection established with {addr}")

                request = receive_all(client_socket).decode()
                request_split = request.split()
                if len(request_split) > 1:
                    method, url = parse_request(request)
                    headers = parse_headers(request)
                    if validating_get_request(request_split):
                        url = request_split[1][1:]
                        if url == '':
                            url = SPARE_URL
                        if validating_param(url):
                            response = definition(url)
                        else:
                            filepath = os.path.join(SITE_FOLDER, url)

                            if "../" not in url:
                                """
                                Specific URLs are checked.

                                If the request contains the URL /forbidden, the server sends a "403 Forbidden" error

                                If the request comes to the /error URL, 
                                the server sends a "500 Internal Server Error" error.

                                If the request comes to the /moved URL, 
                                the server sends "302 Moved Temporarily" as well as the site location.

                                Otherwise, the server serves the requested file or sends a "400 Bad Request"
                                if the request contains an error.
                                """

                                if specific(url):
                                    response = searching_url(url)

                                else:
                                    response = serve_file(filepath)
                            else:
                                response = request_error

                    elif validating_post_request(request_split):
                        response = post_request(client_socket, url, headers)
                    else:
                        response = request_error

                else:
                    response = request_error
                client_socket.sendall(response)

            except socket.error as err:
                """
                Send the name of error in error situation
                """
                print('received socket error on server socket' + str(err))

            finally:
                """
                Close the socket anyway
                """
                client_socket.close()

    except socket.error as err:
        """
        Send the name of error in error situation
        """
        print('received socket error on server socket' + str(err))

    finally:
        """
        Close the socket anyway
        """
        server_socket.close()


if __name__ == "__main__":
    """
    checking function situations and launching the main
    """
    assert specific('error')
    assert specific('forbidden')
    assert specific('moved')
    assert not specific('abc')
    assert searching_url('error')
    assert not searching_url('abc')
    assert choosing_type('jpg')
    assert validating_get_request(['GET', '/', 'HTTP/1.1', 'headers'])
    assert not validating_get_request(['POST', '/', 'HTTP/1.1', 'headers'])
    assert validating_post_request(['POST', '/', 'HTTP/1.1', 'headers'])
    assert not validating_post_request(['not_post', '/', 'HTTP/1.1', 'headers'])
    assert step_over('calculate-next?num=1')
    assert calculating_area('calculate-area?height=2&width=3')
    assert getting_path('image?image-name=abstract.jpg')
    assert validating_param('calculate-next?num=5')
    assert not validating_param('js/submit.js')
    assert parse_headers('GET /imgs/favicon.ico HTTP/1.1\r\nHost: 127.0.0.1\r\n''Connection: keep-alive\r\n'
                         'sec-ch-ua: "Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"\r\n'
                         'sec-ch-ua-mobile: ?0')
    assert not parse_headers('GET /imgs/favicon.ico HTTP/1.1\nHost: 127.0.0.1\n''Connection: keep-alive\n'
                             'sec-ch-ua: "Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"\n'
                             'sec-ch-ua-mobile: ?0')
    assert parse_request('GET /imgs/favicon.ico HTTP/1.1\r\nHost: 127.0.0.1\r\n''Connection: keep-alive\r\n'
                         'sec-ch-ua: "Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"\r\n'
                         'sec-ch-ua-mobile: ?0')
    assert definition('calculate-next?num=1')
    assert definition('calculate-area?height=2&width=3')
    assert definition('image?image-name=abstract.jpg')
    assert not definition('')
    assert validating_param('calculate-next?num=5')
    assert not validating_param('js/submit.js')
    assert getting_path('image?image-name=abstract.jpg')
    assert calculating_area('calculate-area?height=2&width=3')
    assert step_over('calculate-next?num=5')
    main()
