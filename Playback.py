import numpy as np
import cv2
from threading import Thread
import time
import configparser

current_milli_time = lambda: int(round(time.time() * 1000))

class Playback:
	def __init__(self, cam_num=0, sec_rec=10, fps_cap=None, config_path="./config.ini"):
		config = configparser.ConfigParser()
		config.read(config_path)
		if "recap" not in config:
			raise ValueError("recap object not in config")
		config = config["recap"]

		self.fps_cap = int(config["fps_cap"]) if "fps_cap" in config else fps_cap
		self.cam_num = int(config["cam_number"]) if "cam_number" in config else cam_num
		self.sec_rec = int(config["seconds"]) if "seconds" in config else sec_rec

		self.cap = cv2.VideoCapture(cam_num)
		self.fps = self.test_fps()
		if self.fps_cap is not None and self.fps > self.fps_cap:
			self.fps = self.fps_cap
			print("Capping frame rate: {}".format(self.fps))
		self.mspf = 1000/self.fps # Get the number of milliseconds between frames to force the frame rate to be equal to fps
		print("Milliseconds per frame capped at: {}".format(self.mspf))
		self.last_time = 0
		self.num_frames = sec_rec * self.fps
		print("Recording {} frames at a fps of {} to recap {} seconds of footage".format(self.num_frames, self.fps, sec_rec))

		self.frame_shape = (int(self.cap.get(4)), int(self.cap.get(3)))

		self.fr = FrameQueue(self.num_frames, self.frame_shape, pad=3, pause_on_read=True)

		self.thread_cap()

	def test_fps(self, test_frames=120):
		start = time.time()
		for i in range(0, test_frames) :
			ret, frame = self.cap.read()
		end = time.time()
		seconds = end - start
		return int(round(test_frames / seconds))

	def thread_cap(self):
		def cap(self):
			while True:
				curr_time = current_milli_time()
				if self.last_time+self.mspf > curr_time:
					time.sleep((curr_time-(self.last_time-self.mspf))/1000)
				self.last_time = current_milli_time()
				ret, frame = self.cap.read()
				self.fr.push(frame)

		thread = Thread(target=cap, args=(self,)) # Use args=() to pass in arguments
		thread.start()

	def save_rec(self, file):
		frames = self.fr.get_frames()
		fourcc = cv2.VideoWriter_fourcc(*'mp4v')
		video = cv2.VideoWriter(file, fourcc, self.fps, (self.fr.frames.shape[2], self.fr.frames.shape[1]))
		for frame_num in range(self.num_frames):
			frame = np.uint8(frames[frame_num])
			video.write(frame)
		video.release()

	def close(self):
		self.cap.release()
		cv2.destroyAllWindows()

class FrameQueue:
	def __init__(self, num_frames, shape, pad=0, pause_on_read=True):
		self.frames = np.zeros(shape=(num_frames+(2*pad) + 1, *shape, 3)) # One extra frame for saving start frame data
		self.pad = pad
		self.num_frames = num_frames + (2*pad)
		self.reading_frames = False
		self.pause_on_read = pause_on_read

		self.frame_count = 0

	def push(self, frame):
		if not self.pause_on_read or not self.reading_frames:
			print("Pushing new frame")
			frame_num = self.frame_count % self.num_frames
			next_frame = (self.frame_count + 1) % self.num_frames
			self.frames[frame_num] = frame
			self.frames[self.num_frames][0][0][0] = next_frame
			self.frame_count += 1

	def get_frames(self):
		self.reading_frames = True
		start_frame = int(self.frames[self.num_frames][0][0][0] - self.pad)
		if self.pad > 0:
			frames = np.copy(self.frames[self.pad:-(self.pad+1)])
		else:
			frames = np.copy(self.frames[:-1]) # Remove metadata frame
		print("Start Frame is at {}. Rolling {}".format(start_frame, -1*start_frame))
		frames = np.roll(frames, -1*start_frame)
		self.reading_frames = False
		return frames