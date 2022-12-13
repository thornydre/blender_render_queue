import sys
import socket
import threading

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QFileDialog, QLineEdit
from PySide6.QtCore import QFile, QTextStream, QObject
from RenderItem import RenderItem
from RenderQueueThread import RenderQueueThread

IP = "127.0.0.1"
PORT = 22159

class BlenderRenderQueue(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)

		self.title = "Blender Render Queue"

		self.render_items = []

		self.thread_done = object()

		self.initUI()

		self.toggleOverridesCommand()

		self.setUpServer()


	def initUI(self):
		self.setWindowTitle(self.title)

		main_widget = QWidget()

		title_label = QLabel(self.title)

		## OVERRIDES PANEL ##
		self.display_overrides_button = QPushButton("Overrides")
		self.display_overrides_button.clicked.connect(self.displayOverridesCommand)

		self.overrides_widget = QWidget()
		overrides_layout = QVBoxLayout()

		self.overrides_checkbox = QCheckBox("Enable overrides")
		self.overrides_checkbox.clicked.connect(self.toggleOverridesCommand)

		max_samples_layout = QHBoxLayout()
		self.max_samples_label = QLabel("Max samples")
		self.max_samples_textfield = QLineEdit("2048")
		max_samples_layout.addStretch()
		max_samples_layout.addWidget(self.max_samples_label)
		max_samples_layout.addWidget(self.max_samples_textfield)

		min_samples_layout = QHBoxLayout()
		self.min_samples_label = QLabel("Min samples")
		self.min_samples_textfield = QLineEdit("0")
		min_samples_layout.addStretch()
		min_samples_layout.addWidget(self.min_samples_label)
		min_samples_layout.addWidget(self.min_samples_textfield)

		time_limit_layout = QHBoxLayout()
		self.time_limit_label = QLabel("Time limit")
		self.time_limit_textfield = QLineEdit("0")
		time_limit_layout.addStretch()
		time_limit_layout.addWidget(self.time_limit_label)
		time_limit_layout.addWidget(self.time_limit_textfield)

		overrides_layout.addWidget(self.overrides_checkbox)
		overrides_layout.addLayout(max_samples_layout)
		overrides_layout.addLayout(min_samples_layout)
		overrides_layout.addLayout(time_limit_layout)

		self.overrides_widget.setLayout(overrides_layout)

		## FILES PANEL ##
		self.add_file_button = QPushButton("Add blend files")
		self.add_file_button.clicked.connect(self.browseBlendFileCommand)

		self.list_layout = QVBoxLayout()

		step_layout = QHBoxLayout()

		step_label = QLabel("Step")

		self.step_textfield = QLineEdit()
		self.step_textfield.setText("1")

		step_layout.addWidget(step_label)
		step_layout.addWidget(self.step_textfield)

		self.render_button = QPushButton("Render")
		self.render_button.clicked.connect(self.startRender)

		main_layout = QVBoxLayout()
		main_layout.addWidget(title_label)
		main_layout.addWidget(self.display_overrides_button)
		main_layout.addWidget(self.overrides_widget)
		main_layout.addWidget(self.add_file_button)
		main_layout.addLayout(self.list_layout)
		main_layout.addLayout(step_layout)
		main_layout.addWidget(self.render_button)
		main_layout.addStretch()

		main_widget.setLayout(main_layout)

		self.setCentralWidget(main_widget)


	def setUpServer(self):
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.setblocking(True)

		self.server_socket.bind((IP, PORT))

		self.server_socket.listen(5)

		self.clients_data = {}


	def browseBlendFileCommand(self):
		blend_files = QFileDialog.getOpenFileNames(caption="Select blend file to render", filter="Blend Files (*.blend);;All Files (*)")

		for blend_file in blend_files[0]:
			render_item = RenderItem(self, blend_file, self.server_socket)

			self.list_layout.addWidget(render_item)

			self.render_items.append(render_item)


	def displayOverridesCommand(self):
		self.overrides_widget.setVisible(not self.overrides_widget.isVisible())


	def toggleOverridesCommand(self):
		buttons_list = [self.max_samples_textfield,
						self.min_samples_textfield,
						self.time_limit_textfield,
						self.max_samples_label,
						self.min_samples_label,
						self.time_limit_label
		]

		for button in buttons_list:
			button.setEnabled(self.overrides_checkbox.isChecked())


	def startRender(self):
		data = {"render_items": [render_item.renderer for render_item in self.render_items if render_item.isChecked()],
				"max_samples": self.max_samples_textfield.text(),
				"min_samples": self.min_samples_textfield.text(),
				"time_limit": self.time_limit_textfield.text(),
				"step": self.step_textfield.text(),
				"overrides": self.overrides_checkbox.isChecked()
		}

		self.render_queue_thread = RenderQueueThread(data)


def main():
	app = QApplication(sys.argv)
	file = QFile("./assets/dark.qss")
	file.open(QFile.ReadOnly | QFile.Text)
	stream = QTextStream(file)
	app.setStyleSheet(stream.readAll())

	widget = BlenderRenderQueue()
	widget.resize(300, 200)
	widget.show()

	sys.exit(app.exec())

if __name__ == "__main__":
	main()
