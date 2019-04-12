from Trigger import Trigger
from Clap import Clap
from Playback import Playback
from threading import Thread
import datetime
import os

config_file = "/Users/aidandempster/projects/2019/spring/knock/config.ini"
video_dir = "/Users/aidandempster/projects/2019/spring/knock/recaps"

if __name__ == "__main__":
	trigger = Trigger(config_path=config_file, timeout=10000)
	play = Playback(sec_rec=15)

	def on_knock():
		print("Knock Triggered")
		trigger.push("Knock on Door")
		file_name = os.path.join(video_dir, "recap-{}.mp4".format(datetime.datetime.now().strftime("%y-%m-%d-%H:%H:%S")))
		play.save_rec(file=file_name)
		trigger.on_recap(file_name)
		trigger.push("Recap Sent")
		print("Finished Sending")

	def test():
		print("Clapped")

	clap_det = Clap(on_knock)