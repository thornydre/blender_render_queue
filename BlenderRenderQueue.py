import subprocess
import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QFileDialog


class BlenderRenderQueue(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)

		self.title = "Blender Render Queue"

		self.render_items = []

		self.initUI()


	def initUI(self):
		self.setWindowTitle(self.title)

		main_widget = QWidget()

		title_label = QLabel(self.title)

		self.add_file_button = QPushButton("Add blend file")
		self.add_file_button.clicked.connect(self.browseBlendFileCommand)

		self.list_layout = QVBoxLayout()

		self.render_button = QPushButton("Render")
		self.render_button.clicked.connect(self.startRender)

		self.vert_layout = QVBoxLayout()
		self.vert_layout.addWidget(title_label)
		self.vert_layout.addWidget(self.add_file_button)
		self.vert_layout.addLayout(self.list_layout)
		self.vert_layout.addWidget(self.render_button)

		main_widget.setLayout(self.vert_layout)

		self.setCentralWidget(main_widget)


	def browseBlendFileCommand(self):
		blend_file = QFileDialog.getOpenFileName(caption="Select blend file to render", filter="Blend Files (*.blend);;All Files (*)")

		if blend_file[0]:
			render_item = RenderItem(blend_file[0])

			self.list_layout.addWidget(render_item)

			self.render_items.append(render_item)


	def startRender(self):
		blender_path = "F:/prog/blender_git/branches/master_branch/bin/Release/blender.exe"
		
		for render_item in self.render_items:
			if render_item.isChecked():
				render_args = [blender_path, "-b", render_item.getPath(), "-j", "1", "-E", "CYCLES", "-a", "--", "--cycles-device", "OPTIX+CPU"]

				proc = subprocess.Popen(render_args)
				proc.wait()

				render_item.setDone(True)


class RenderItem(QWidget):
	def __init__(self, file_path, *args, **kwargs):
		super(RenderItem, self).__init__(*args, **kwargs)

		self.checked = True
		self.file_path = file_path
		self.done = False

		self.initUI()


	def initUI(self):
		layout = QHBoxLayout()

		checked_checkbox = QCheckBox()
		checked_checkbox.setChecked(self.checked)

		file_path_label = QLabel(self.file_path)

		self.done_checkbox = QCheckBox()
		self.done_checkbox.setChecked(self.done)

		remove_button = QPushButton("Remove")
		remove_button.clicked.connect(self.removeCommand)

		layout.addWidget(checked_checkbox)
		layout.addWidget(file_path_label)
		layout.addWidget(self.done_checkbox)
		layout.addWidget(remove_button)

		self.setLayout(layout)


	def removeCommand(self):
		self.deleteLater()
		self.checked = False


	def isChecked(self):
		return self.checked


	def getPath(self):
		return self.file_path


	def setDone(self, done):
		self.done = done
		self.done_checkbox.setChecked(self.done)


def main():
	app = QApplication(sys.argv)
	# file = QFile("./assets/dark.qss")
	# file.open(QFile.ReadOnly | QFile.Text)
	# stream = QTextStream(file)
	# app.setStyleSheet(stream.readAll())

	widget = BlenderRenderQueue()
	widget.resize(300, 200)
	widget.show()

	sys.exit(app.exec())

if __name__ == "__main__":
	main()
