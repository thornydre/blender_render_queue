from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QFileDialog, QLineEdit, QProgressBar
from RenderThread import RenderThread
from RenderItemRenderer import RenderItemRenderer
from subprocess import Popen
import pickle

HEADER_LENGTH = 10

class RenderItem(QWidget):
	def __init__(self, parent, file_path, server_socket, *args, **kwargs):
		super(RenderItem, self).__init__(*args, **kwargs)

		self.parent = parent
		self.file_path = file_path
		self.done = False

		self.server_socket = server_socket
		blend_info = self.getBlendInfo()

		self.initUI()

		self.render_thread = RenderThread(blend_info["start_frame"], blend_info["end_frame"])
		self.render_thread.progression_signal.connect(self.progress_bar.setValue)

		self.renderer = RenderItemRenderer(self.file_path, self.render_thread)


	def initUI(self):
		main_layout = QVBoxLayout()

		line1_layout = QHBoxLayout()

		self.checked_checkbox = QCheckBox()
		self.checked_checkbox.setChecked(True)

		file_path_label = QLabel(self.file_path)

		remove_button = QPushButton("Remove")
		remove_button.clicked.connect(self.removeCommand)

		line1_layout.addWidget(self.checked_checkbox)
		line1_layout.addWidget(file_path_label)
		line1_layout.addWidget(remove_button)

		self.progress_bar = QProgressBar()
		self.progress_bar.setRange(0, 100)
		self.progress_bar.setValue(0)

		main_layout.addLayout(line1_layout)
		main_layout.addWidget(self.progress_bar)

		self.setLayout(main_layout)


	def getBlendInfo(self):
			blender_path = "F:/prog/blender_git/branches/master_branch/bin/Release/blender.exe"

			render_args = [blender_path, "-b", self.file_path, "--python", "SendBlendInfo.py"]

			Popen(render_args)

			client_socket, client_address = self.server_socket.accept()

			blend_info = self.receiveData(client_socket)

			if not blend_info:
				return None

			return blend_info


	def receiveData(self, client_socket):
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


	def removeCommand(self):
		self.parent.render_items.remove(self)
		self.deleteLater()
		self.checked_checkbox.setChecked(False)


	def isChecked(self):
		return self.checked_checkbox.isChecked()


	def getPath(self):
		return self.file_path
