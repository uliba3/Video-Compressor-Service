import socket
import json
import os, ffmpeg
import io

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 14000

def compress_video(input_path, output_path, crf=23):
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, vcodec='libx265', crf=28)
            .overwrite_output()
            .run()
        )
        print("Compression successful!")
    except ffmpeg.Error as e:
        print(f"Error during compression: {e.stderr}")


def change_resolution(input_video_bytes, resolution='640x480'):
    output_video_buffer = io.BytesIO()
    (
        ffmpeg
        .input('pipe:', f='mp4', r=30)
        .output('pipe:', f='mp4', vf='scale='+resolution)
        .run(input=input_video_bytes)
    )
    return output_video_buffer.getvalue()

def change_aspect_ratio(input_video_bytes, aspect_ratio='16:9'):
    output_video_buffer = io.BytesIO()
    (
        ffmpeg
        .input('pipe:', f='mp4', r=30)
        .output('pipe:', f='mp4', vf='setsar='+aspect_ratio)
        .run(input=input_video_bytes)
    )
    return output_video_buffer.getvalue()

def operate(parameters, file, file_path="inputServer.mp4", output_file_name="outputServer.mp4"):
    #compress
    if(parameters["operation"] == 1):
        print("compressing...")
        compress_video(file_path, output_file_name)
    #change resolution
    elif(parameters["operation"] == 2):
        print("changing resolution...")
        return change_resolution(file)
    #change aspect ratio
    elif(parameters["operation"] == 3):
        print("changing aspect ratio...")
        return change_aspect_ratio(file)

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        #connect with client
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(1)
        print("Waiting for server to connect...")
        client_socket, client_address = server_socket.accept()
        print(f"Client {client_address} connected.")

        #receive data size
        header = client_socket.recv(64)
        parameters_size = int.from_bytes(header[:16], byteorder='big')
        print(f"parameters size: {parameters_size}")
        file_size = int.from_bytes(header[16:], byteorder='big')
        print(f"file size: {file_size} bytes")

        inputfile = bytes()
        #receive data itself
        data = client_socket.recv(parameters_size)
        parameters = json.loads(data.decode())
        while data:
            data = client_socket.recv(BUFFER_SIZE)
            inputfile += data
            print(f"received {len(data)} bytes")
            if len(data) < BUFFER_SIZE:
                break

        #save file to server
        with open("inputServer.mp4", 'wb') as file:
            file.write(inputfile)
            print("inputServer.mp4 created")
            #print("file:", inputfile)

        operate(parameters, inputfile)

        #convert ouput file to bytes
        with open("outputServer.mp4", 'rb') as file:
            data = file.read(BUFFER_SIZE)
            client_socket.send(data)
            while len(data) == BUFFER_SIZE:
                data = file.read(BUFFER_SIZE)
                print(f"sent {len(data)} bytes")
                client_socket.send(data)

if __name__ == "__main__":
    start_server()
