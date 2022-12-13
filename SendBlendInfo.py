#!/usr/bin/python

import bpy
import os
import socket
import select
import pickle


class Client():
	def __init__(self):
		self.header_length = 10
		self.ip = "127.0.0.1"
		self.port = 22159

		try:
			self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.client_socket.settimeout(2)
			self.client_socket.connect((self.ip, self.port))
			self.client_socket.settimeout(None)
		except TimeoutError as e:
			print("CONNECTION TO SERVER TIMED OUT")
			print(e)
		except socket.timeout as e:
			print("CONNECTION TO SERVER TIMED OUT")
			print(e)
		

	def sendData(self, data):
		sent_data = pickle.dumps(data)
		data_header = f"{len(sent_data):<{self.header_length}}".encode("utf-8")

		try:
			self.client_socket.send(data_header + sent_data)

		except ConnectionResetError as e:
			print("Lost connection to the server")
			sys.exit()


client = Client()

info = {
	"device": bpy.context.scene.cycles.device,
	"max_sample": bpy.context.scene.cycles.samples,
	"resx": bpy.context.scene.render.resolution_x,
	"resy": bpy.context.scene.render.resolution_y,
	"start_frame": bpy.context.scene.frame_start,
	"end_frame": bpy.context.scene.frame_end
}

client.sendData(info)

bpy.ops.wm.quit_blender()