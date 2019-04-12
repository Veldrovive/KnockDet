import pyaudio
import sys
from threading import Thread
from time import sleep
from array import array	

class Clap:
	def __init__(self, callback=None):
		if callback is None:
			self.callback = self.alert
		else:
			self.callback = callback

		self.chunk = 1024
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = 1
		self.RATE = 44100
		self.threshold = 30000
		self.max_value = 0
		self.p = pyaudio.PyAudio()

		self.clap = 0
		self.state = 0
		self.wait = 2
		self.clap_thresh = 3

		self.start()

	def alert(self):
		print("Knock Detected")

	def start(self):
		self.main_proc = Thread(target=self.start_det)
		self.main_proc.start()

	def open_stream(self):
		stream = self.p.open(format=self.FORMAT,
			channels=self.CHANNELS, 
			rate=self.RATE, 
			input=True,
			output=True,
			frames_per_buffer=self.chunk)
		return stream

	def start_det(self):
		stream = self.open_stream()
		try:
			print("Clap detection initialized")
			while True:
				data = stream.read(self.chunk, exception_on_overflow=False)
				as_ints = array('h', data)
				self.max_value = max(as_ints)
				if self.max_value > self.threshold:
					self.clap += 1
				if self.clap == 1 and self.state == 0:
					thread = Thread(target=self.waitForClaps, args=("waitThread",))
					thread.start()
					self.state = 1
		except (KeyboardInterrupt, SystemExit):
			print("\rExiting")
			stream.stop_stream()
			stream.close()
			self.p.terminate()

	def waitForClaps(self, threadName):
		sleep(self.wait)
		if self.clap >= self.clap_thresh:
			self.callback()
		self.clap = 0
		self.state = 0


# if __name__ == '__main__':
# 	main()