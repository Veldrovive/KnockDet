import numpy as np
import cv2
from threading import Thread
import time

class Playback:
	def __init__(self, cam_num=0, sec_rec=10, fps=None):
		self.cap = cv2.VideoCapture(cam_num)
		self.fps = self.test_fps() if fps is None else fps
		self.num_frames = int(round(sec_rec * self.fps)) + 6 # Add 3 frames of padding on each side
		print("Recording {} frames at a fps of {} to recap {} seconds of footage".format(self.num_frames, self.fps, sec_rec))

		#self.frames = np.zeros(shape=(self.num_frames+1, int(self.cap.get(4)), int(self.cap.get(3)), 3)) # This system doesn't work for some reason. I guess O(n) is good enough
		self.frames = np.zeros(shape=(self.num_frames, int(self.cap.get(4)), int(self.cap.get(3)), 3))

		self.thread_cap()

	def test_fps(self, test_frames=120):
		start = time.time()
		for i in range(0, test_frames) :
			ret, frame = self.cap.read()
		end = time.time()
		seconds = end - start
		return test_frames / seconds


	def thread_cap(self):
		def cap(self):
			frame_count = 0
			while True:
				frame_num = frame_count % self.num_frames
				next_frame = (frame_count + 1) % self.num_frames
				ret, frame = self.cap.read()
				self.frames[frame_num] = frame
				self.frames[next_frame] = np.zeros(shape=self.frames.shape[1:])
				#self.frames[self.num_frames][0][0][0] = next_frame # System doesnt work
				frame_count += 1

		thread = Thread(target=cap, args=(self,)) # Use args=() to pass in arguments
		thread.start()

	def save_rec(self, file="/Users/aidandempster/projects/2019/spring/knock/recall.mov"):
		frames = np.copy(self.frames)
		for start_frame, frame in enumerate(frames):
			if not frame.any():
				break
		#start_frame = frames[self.num_frames][0][0][0] # System doesnt work
		fourcc = cv2.VideoWriter_fourcc(*'mp4v')
		video = cv2.VideoWriter(file, fourcc, round(self.fps), (self.frames.shape[2], self.frames.shape[1]))
		for i in range(start_frame+3, start_frame+len(self.frames)-3): # Remove Padding frames for corruption
			frame_num = i % self.num_frames
			frame = np.uint8(frames[frame_num])
			video.write(frame)
		video.release()
		print("Recap Saved")

	def thread_save(self, file="/Users/aidandempster/projects/2019/spring/knock/recall.mov"):
		thread = Thread(target=self.save_rec, args=(file,))
		thread.start()

	def close(self):
		self.cap.release()
		cv2.destroyAllWindows()