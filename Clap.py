import pyaudio
import sys
from threading import Thread
from time import sleep
from array import array	
from ctypes import *
from contextlib import contextmanager
import configparser

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

class Clap:
	def __init__(self, callback_map={}, default_callback=None, config_path="./config.ini"):
		config = configparser.ConfigParser()
		config.read(config_path)
		if "knock" not in config:
			raise ValueError("recap object not in config")
		config = config["knock"]

		if default_callback is None:
			self.default_callback = self.alert
		else:
			self.default_callback = default_callback
		self.callback_map = callback_map

		self.chunk = 1024
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = 1
		self.RATE = 44100
		self.threshold = int(config["threshold"]) if "threshold" in config else 1000
		print("Using a knock threshold of: {}".format(self.threshold))
		self.max_value = 0
		try:
			with noalsaerr():
				self.p = pyaudio.PyAudio()
		except OSError:
			self.p = pyaudio.PyAudio()

		self.clap = 0
		self.state = 0
		self.wait = 2
		self.clap_thresh = 3

		self.device_keywords = ["usb"]

		self.start()

	def find_input_device(self, keywords=[], verbose=False):
		device_index = None
		for i in range(self.p.get_device_count()):
			devinfo = self.p.get_device_info_by_index(i)
			if verbose:
				print("Device {}: {}".format(i, devinfo["name"]))

			if len(keywords) == 0:
				device_index = i
			else:
				for keyword in keywords:
					if keyword in devinfo["name"].lower():
						if verbose:
							print("{} is a matching device".format(devinfo["name"]))
						device_index = i
		if device_index is None:
			print("Using default device")
		else:
			devinfo = self.p.get_device_info_by_index(device_index) 
			print("Using {}: {}".format(device_index, devinfo["name"]))

		return device_index

	def alert(self):
		print("Knock Detected")

	def start(self):
		self.main_proc = Thread(target=self.start_det)
		self.main_proc.start()

	def open_stream(self):
		device_index = self.find_input_device(keywords=self.device_keywords)

		stream = self.p.open(
			format=self.FORMAT,
			channels=self.CHANNELS, 
			rate=self.RATE, 
			input=True,
			output=True,
			input_device_index = device_index,
			frames_per_buffer=self.chunk
		)
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
		if self.clap in self.callback_map:
			callback = self.callback_map[self.clap]
			callback()
		else:
			self.default_callback()
		self.clap = 0
		self.state = 0


# if __name__ == '__main__':
# 	main()
