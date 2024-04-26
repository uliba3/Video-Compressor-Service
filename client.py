import socket
import json
import ffmpeg

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 14000

def send_file():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        #connect to server
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("connected to server")

        #file input
        file_path = "test.mp4"
        parameters = ffmpeg.probe(file_path)
        print("parameters:", parameters)
        parameters["operation"] = 3

        #send data size
        parameters_size = len(json.dumps(parameters).encode())
        file_size = len(open(file_path, 'rb').read())
        client_socket.send(parameters_size.to_bytes(16, byteorder='big')+file_size.to_bytes(48, byteorder='big'))
        print("parametrs size:", parameters_size)
        print("file size:", file_size)

        #send data itself
        body = json.dumps(parameters).encode()
        sum = 0
        with open(file_path, 'rb') as file:
            data = body
            client_socket.send(data)
            while data:
                data = file.read(BUFFER_SIZE)
                sum += len(data)
                print("data sent: {0} bytes".format(sum))
                client_socket.send(data)
                if len(data) < BUFFER_SIZE:
                    break

        #receive output file
        file = bytes()
        data = client_socket.recv(BUFFER_SIZE)
        file += data
        while len(data) == BUFFER_SIZE:
            data = client_socket.recv(BUFFER_SIZE)
            file += data
            print(f"received {len(data)} bytes")

        with open("outputClient.mp4", 'wb') as output_file:
            output_file.write(file)
            print("output.mp4 created")
            #print("file:", file)

if __name__ == "__main__":
    send_file()
