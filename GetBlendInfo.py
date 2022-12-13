#!/usr/bin/python

import os
import socket
import select
import pickle
import threading

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 22159

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.setblocking(True)

server_socket.bind((IP, PORT))

server_socket.listen(5)

clients_data = {}


def receiveData(client_socket):
	try:
		data_header = client_socket.recv(HEADER_LENGTH)

		if not len(data_header):
			return False

		data_length = int(data_header.decode("utf-8").strip())

		data = client_socket.recv(data_length)

		return pickle.loads(data)

	except Exception as e:
		print(e)
		return False


def control():
	while True:
		command = input()
		if command == "exit()":
			for socket in clients_data:
				socket.close()
			os._exit(0)


def threaded_client(client_socket, client_address):
		blend_info = receiveData(client_socket)

		if not blend_info:
			return

		print(blend_info)

		return


control_thread = threading.Thread(target=control)
control_thread.start()

while True:
	client_socket, client_address = server_socket.accept()

	client_thread = threading.Thread(target=threaded_client, args=(client_socket, client_address))
	client_thread.start()