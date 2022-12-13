from subprocess import PIPE, Popen
from threading import Thread


class RenderItemRenderer:
	def __init__(self, file_path, thread):
		self.file_path = file_path

		self.thread = thread


	def render(self, step, script):
		blender_path = "F:/prog/blender_git/branches/master_branch/bin/Release/blender.exe"

		render_args = [blender_path, "-b", self.file_path, "--python-expr", script, "--addons", "path_maker", "-j", step, "-E", "CYCLES", "-a", "--", "--cycles-device", "OPTIX+CPU"]

		proc = Popen(render_args, stdout=PIPE)

		self.thread.start(proc)
