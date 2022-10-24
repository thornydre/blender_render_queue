import sys

from subprocess import PIPE, Popen
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QFileDialog, QLineEdit, QProgressBar
from PySide6.QtCore import QFile, QTextStream, Signal
from threading  import Thread


class BlenderRenderQueue(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)

		self.title = "Blender Render Queue"

		self.render_items = []

		self.thread_done = object()

		self.initUI()

		self.toggleOverridesCommand()


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

		self.stop_render_button = QPushButton("Stop Render")
		self.stop_render_button.clicked.connect(self.stopRender)

		main_layout = QVBoxLayout()
		main_layout.addWidget(title_label)
		main_layout.addWidget(self.display_overrides_button)
		main_layout.addWidget(self.overrides_widget)
		main_layout.addWidget(self.add_file_button)
		main_layout.addLayout(self.list_layout)
		main_layout.addLayout(step_layout)
		main_layout.addWidget(self.render_button)
		main_layout.addWidget(self.stop_render_button)
		main_layout.addStretch()

		main_widget.setLayout(main_layout)

		self.setCentralWidget(main_widget)


	def browseBlendFileCommand(self):
		blend_files = QFileDialog.getOpenFileNames(caption="Select blend file to render", filter="Blend Files (*.blend);;All Files (*)")

		for blend_file in blend_files[0]:
			render_item = RenderItem(blend_file)

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
		blender_path = "F:/prog/blender_git/branches/master_branch/bin/Release/blender.exe"
		blender_path = "C:/Program Files/Blender Foundation/Blender 3.2/blender.exe"
		
		for render_item in self.render_items:
			if render_item.isChecked():
				script = "import bpy\n"

				if self.overrides_checkbox.isChecked():
					script += f"bpy.context.scene.cycles.samples = {self.max_samples_textfield.text()}\n"
					script += f"bpy.context.scene.cycles.adaptive_min_samples = {self.min_samples_textfield.text()}\n"

					script += f"bpy.context.scene.cycles.time_limit = {self.time_limit_textfield.text()}\n"

				render_args = [blender_path, "-b", render_item.getPath(), "--python-expr", script, "-j", self.step_textfield.text(), "-E", "CYCLES", "-a", "--", "--cycles-device", "OPTIX+CPU"]

				proc = Popen(render_args, stdout=PIPE, bufsize=1)
				self.stop_thread = False
				self.render_thread = Thread(target=self.enqueueOutput, args=(lambda:self.stop_thread, proc.stdout, render_item), daemon=True)
				self.render_thread.start()


	def stopRender(self):
		self.stop_thread = True
		self.render_thread.join()


	def enqueueOutput(self, stop_thread, out, render_item):
		for byte_line in iter(out.readline, b""):
			line = byte_line.decode("utf-8")
			print(line)
			samples = line.split("|")[-1].lower()
			if "sample" in samples:
				percent = eval(samples.split()[-1]) * 100
				# print(percent)
				render_item.setProgress(percent)
		out.close()

		render_item.setProgress(1.0)
		render_item.setDone(True)


class RenderItem(QWidget):
	def __init__(self, file_path, *args, **kwargs):
		super(RenderItem, self).__init__(*args, **kwargs)

		self.file_path = file_path
		self.done = False
		self.progress_changed = Signal(int)

		self.initUI()


	def initUI(self):
		main_layout = QVBoxLayout()

		line1_layout = QHBoxLayout()

		self.checked_checkbox = QCheckBox()
		self.checked_checkbox.setChecked(True)

		file_path_label = QLabel(self.file_path)

		self.done_checkbox = QCheckBox()
		self.done_checkbox.setChecked(self.done)

		remove_button = QPushButton("Remove")
		remove_button.clicked.connect(self.removeCommand)

		line1_layout.addWidget(self.checked_checkbox)
		line1_layout.addWidget(file_path_label)
		line1_layout.addWidget(self.done_checkbox)
		line1_layout.addWidget(remove_button)

		self.progress_bar = QProgressBar()
		self.progress_bar.setRange(0.0, 100.0)
		self.progress_changed.connect(self.progress_bar.setValue)

		main_layout.addLayout(line1_layout)
		main_layout.addWidget(self.progress_bar)

		self.setLayout(main_layout)


	def removeCommand(self):
		self.deleteLater()
		self.checked_checkbox.setChecked(False)


	def isChecked(self):
		return self.checked_checkbox.isChecked()


	def getPath(self):
		return self.file_path


	def setDone(self, done):
		self.done_checkbox.setChecked(True)


	def setProgress(self, value):
		self.progress_changed.emit(value)


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
