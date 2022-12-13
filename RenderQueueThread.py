from PySide6.QtCore import QObject
from threading  import Thread


class RenderQueueThread(QObject):
	def __init__(self, data, *args, **kwargs):
		super(RenderQueueThread, self).__init__(*args, **kwargs)

		self.thread = Thread(target=self.run, args=(data, ), daemon=True)
		self.thread.start()


	def run(self, data):
		for render_item in data['render_items']:
			script = "import bpy\n"

			if data['overrides']:
				script += f"bpy.context.scene.cycles.samples = {data['max_samples']}\n"
				script += f"bpy.context.scene.cycles.adaptive_min_samples = {data['min_samples']}\n"
				script += f"bpy.context.scene.cycles.time_limit = {data['time_limit']}\n"

			render_item.render(data['step'], script)
