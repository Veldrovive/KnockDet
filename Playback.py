import numpy as np
import cv2
from threading import Thread
import time

class Playback:
	def __init__(self, cam_num=0, sec_rec=10, fps=None):
		self.cap = cv2.VideoCapture(cam_num)
		self.fps = self.test_fps() if fps is None else fps
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

	def thread_save(self, file="/Users/aidandempster/projects/2019/spring/knock/recall.mov"):
		thread = Thread(target=self.save_rec, args=(file,))
		thread.start()

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