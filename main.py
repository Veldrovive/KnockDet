from Trigger import Trigger
from Clap import Clap
from Playback import Playback
from threading import Thread
import datetime
import os

config_file = "./config.ini"
video_dir = "./recaps"

if __name__ == "__main__":
	trigger = Trigger(config_path=config_file, timeout=10000)
	play = Playback(sec_rec=5, cam_num=0, config_path=config_file)

	def send_notif_recap():
		print("Knock Triggered")
		trigger.push("Knock on Door - Sending Recap")
		file_name = os.path.join(video_dir, "recap-{}.mp4".format(datetime.datetime.now().strftime("%y-%m-%d-%H:%H:%S")))
		play.save_rec(file=file_name)
		trigger.on_recap(file_name)
		print("Finished Sending")

	def send_knock_notif():
		print("Notif Triggered")
		trigger.push("Knock on Door - No Recap")


	def test():
		print("Clapped")

	knock_map = {
		1: test,
		2: test,
		3: send_knock_notif,
		4: send_knock_notif
	}

	clap_det = Clap(knock_map, send_notif_recap, config_path=config_file) # If more than 4 knocks are detected, send a recap
