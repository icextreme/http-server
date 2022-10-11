import os
from socket import *
from email.utils import formatdate

# Common port for web server
PORT = 8080
TIMEOUT = 5

# Response messages
HTTP_OK = "HTTP/1.1 200 OK\r\n"
HTTP_NOT_MODIFIED = "HTTP/1.1 304 Not Modified\r\n"
HTTP_BAD_REQUEST = "HTTP/1.1 400 Bad Request\r\n"
HTTP_NOT_FOUND = "HTTP/1.1 404 Not Found\r\n"
HTTP_REQUEST_TIMED_OUT = "HTTP/1.1 408 Request Timed Out\r\n"


def run():
    # Create TCP socket, bind to localhost, and listen
    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.bind(("localhost", PORT))
    server_sock.listen(1)

    print("The server is ready for connection.\n")

    while True:
        # Server accepts TCP connection
        (connection_sock, addr) = server_sock.accept()

        # Set timeout to 5 seconds
        connection_sock.settimeout(TIMEOUT)

        print("Connection accepted")

        try:
            # Decode received message
            message = connection_sock.recv(1024).decode()

            # Log HTTP request message
            print(message)

            request = message.split()[0]
            # print(request)

            if request == "GET":
                response_get(connection_sock, message)
            else:
                response_http_bad_request(connection_sock)

        except timeout:
            response_http_request_timed_out(connection_sock)
            print("Sent request timed out error\n")
            
        except:
            # Send HTTP not found when error
            response_http_not_found(connection_sock)

        finally:
            connection_sock.close()


def response_get(connection_sock, message):
    # GET /test.html HTTP/1.1
    # Split message by whitespace
    file_name = message.split()[1]  # "/test.html"
    # print(file_name)

    # Strip "/" from "/test.html" and open file
    file = open(file_name[1:])

    # Read file into output buffer
    output_buf = file.read()

    path = os.path.join(os.getcwd(), file_name[1:])
    last_modified_date = formatdate(os.path.getmtime(path))

    last_modified_header = "Last-Modified: " + last_modified_date + "\r\n"

    # Check for If-Modified-Since in header
    if "If-Modified-Since" in message:
        if_modified_date = message.split("If-Modified-Since: ")[1].split("\r\n")[0]

        # Send HTTP Last Modified if dates are same
        if last_modified_date == if_modified_date:
            response_http_not_modified(connection_sock)
        else:
            response_http_ok(connection_sock)
            connection_sock.send(last_modified_header.encode())
    else:
        response_http_ok(connection_sock)

        connection_sock.send(last_modified_header.encode())
        connection_sock.send("\r\n".encode())

        # Send file from output buffer
        connection_sock.send(output_buf.encode())

    # Close file after sending
    file.close()


def response_http_ok(connection_sock):
    # Send HTTP header and end of header indication
    connection_sock.send(HTTP_OK.encode())
    # Header not sent in case of extra header info


def response_http_not_modified(connection_sock):
    connection_sock.send(HTTP_NOT_MODIFIED.encode())
    connection_sock.send("\r\n".encode())


def response_http_bad_request(connection_sock):
    connection_sock.send(HTTP_BAD_REQUEST.encode())
    connection_sock.send("\r\n".encode())


def response_http_not_found(connection_sock):
    connection_sock.send(HTTP_NOT_FOUND.encode())

    # Indicate end of header
    connection_sock.send("\r\n".encode())

    connection_sock.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())


def response_http_request_timed_out(connection_sock):
    connection_sock.send(HTTP_REQUEST_TIMED_OUT.encode())
    connection_sock.send("\r\n".encode())


if __name__ == '__main__':
    run()
