from PySide6.QtCore import QObject, Signal
from threading  import Thread


class RenderThread(QObject):
	progression_signal = Signal(int)

	def __init__(self, start_frame, end_frame, *args, **kwargs):
		super(RenderThread, self).__init__(*args, **kwargs)

		self.start_frame = start_frame
		self.end_frame = end_frame
		self.range = end_frame - start_frame + 1


	def start(self, proc):
		self.thread = Thread(target=self.run, args=(proc.stdout, ), daemon=True)
		self.thread.start()
		self.thread.join()


	def run(self, out):
		for byte_line in iter(out.readline, b""):
			line = byte_line.decode("utf-8")
			print(line)

			info = self.getInfoFromLine(line)

			if info:
				current_frame_percent = info["samples"][0] / info["samples"][1] / self.range
				total_frames_percent = (info["frame"] - self.start_frame) / self.range
				percent = (total_frames_percent + current_frame_percent) * 100
				print(percent)
				self.progression_signal.emit(percent)
		out.close()

		self.progression_signal.emit(100)


	def getInfoFromLine(self, line):
		info = {}
		info_list = line.split("|")

		if len(info_list) != 6:
			return None

		samples_string = info_list[-1].lower()
		if "sample" in samples_string:
			div = samples_string.split()[-1]
			info["samples"] = [float(i) for i in div.split("/")]
		else:
			return None

		frame_string = info_list[0].split()[0]
		if "Fra" in frame_string:
			info["frame"] = float(frame_string.split(":")[-1])
		else:
			return None

		return info
