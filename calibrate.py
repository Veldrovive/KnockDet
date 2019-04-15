import pyaudio
from array import array	
from threading import Thread
import time
import numpy as np

p = pyaudio.PyAudio()

def find_input_device(keywords=[], verbose=False):
		device_index = None  
		for i in range(p.get_device_count()):
			devinfo = p.get_device_info_by_index(i)
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
			devinfo = p.get_device_info_by_index(device_index) 
			print("Using {}: {}".format(device_index, devinfo["name"]))

		return device_index

def open_stream(params, device_index):
		stream = p.open(
			format=params["FORMAT"],
			channels=params["CHANNELS"], 
			rate=params["RATE"], 
			input=True,
			output=True,
			input_device_index=device_index,
			frames_per_buffer=params["chunk"]
		)
		return stream

max_arr = []
amb_arr = []
recording_max = False
exit = False
def start_det(stream, chunk):
	global amb_arr
	global recording_max
	global max_arr
	global exit
	try:
		print("Clap detection initialized")
		while True:
			data = stream.read(chunk, exception_on_overflow=False)
			as_ints = array('h', data)
			max_value = max(as_ints)
			if recording_max:
				max_arr.append(max_value)
			else:
				amb_arr.append(max_value)
			if exit:
				raise SystemExit
	except (KeyboardInterrupt, SystemExit):
		stream.stop_stream()
		stream.close()
		p.terminate()

def test(knock=5, talk=3, standard=0):
	global amb_arr
	global recording_max
	global max_arr
	global exit
	if knock > 0:
		maxes = []
		print("\nTesting Knocking:")
		time.sleep(1.5)
		for i in range(knock):
			for val in max_arr:
				max_arr.remove(val)
			print("Test: {}".format(i+1))
			print("Knock in -")
			print("3.")
			time.sleep(1)
			print("2.")
			time.sleep(1)
			print("1.")
			time.sleep(0.9)
			recording_max = True
			time.sleep(0.1)
			print("Knock!\n")
			time.sleep(1.5)
			recording_max = False
			maxes.append(max(max_arr))
			time.sleep(1)

		knock_sd = np.std(maxes)
		knock_mean = np.mean(maxes)
		knock_min = knock_mean-2.5*knock_sd

	if talk > 0:
		maxes = []
		print("\nTesting Talking:")
		time.sleep(1.5)
		for i in range(talk):
			for val in max_arr:
				max_arr.remove(val)
			print("Test: {}".format(i+1))
			print("Start talking in -")
			print("3.")
			time.sleep(1)
			print("2.")
			time.sleep(1)
			print("1.")
			time.sleep(0.9)
			recording_max = True
			time.sleep(0.1)
			print("Talk!\n")
			time.sleep(3)
			recording_max = False
			print("Stop talking")
			maxes.append(max(max_arr))
			time.sleep(1)

		talk_sd = np.std(maxes)
		talk_mean = np.mean(maxes)
		talk_max = talk_mean+2.5*talk_sd

	if standard > 0:
		maxes = []
		print("Testing Standard:")
		time.sleep(1.5)
		for i in range(standard):
			for val in max_arr:
				max_arr.remove(val)
			print("Test: {}".format(i+1))
			print("Start doing your usual stuff in -")
			print("3.")
			time.sleep(1)
			print("2.")
			time.sleep(1)
			print("1.")
			time.sleep(0.9)
			recording_max = True
			time.sleep(0.1)
			print("Start!\n")
			time.sleep(10)
			recording_max = False
			print("Stop")
			maxes.append(max(max_arr))
			time.sleep(1)

		std_sd = np.std(maxes)
		std_mean = np.mean(maxes)
		std_max = std_mean+2.5*std_sd


	amb_sd = np.std(amb_arr)
	amb_mean = np.mean(amb_arr)
	amb_max = amb_mean+2.5*amb_sd

	print("Mean ambient volume was {} with a standard dev of {}.\nThe expected maximum volume of ambient sound is {}.\n".format(int(round(amb_mean)), int(round(amb_sd)), int(round(amb_max))))
	if talk > 0:
		print("Talking:")
		print("Mean value of talking was {} and standard dev was {}.\nThe maximum expected volume of talking is {}.\n".format(int(round(talk_mean)), int(round(talk_sd)), int(round(talk_max))))
	if standard > 0:
		print("Standard:")
		print("Mean value of tests was {} and standard dev was {}.\nThe maximum expected value of standard life is {}.\n".format(int(round(std_mean)), int(round(std_sd)), int(round(std_max))))
	print("Knocking:")
	print("Mean value of tests was {} and standard dev was {}.\nThe suggested value for threshold is {}.".format(int(round(knock_mean)), int(round(knock_sd)), int(round(knock_min))))
	exit = True
	


if __name__ == "__main__":
	knock_test_num = int(input("How many tests for knocking should be done? "))
	talk_test_num = int(input("How many tests for talking should be done? "))
	life_test_num = int(input("How many tests of standard sound should be done? "))

	device_index = find_input_device(keywords=["usb"], verbose=True)
	chunk = 1024
	params = {
		"FORMAT": pyaudio.paInt16,
		"CHANNELS": 1,
		"RATE": 44100,
		"chunk": chunk,
	}
	stream = open_stream(params, device_index)
	thread = Thread(target=start_det, args=(stream, chunk, ))
	thread.start()
	test(knock_test_num, talk_test_num, life_test_num)
