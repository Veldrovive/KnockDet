import smtplib
import configparser
import time
import datetime
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

current_milli_time = lambda: int(round(time.time() * 1000))

class Trigger:
	def __init__(self, config_path="./config.ini", timeout=5000):
		config = configparser.ConfigParser()
		config.read(config_path)
		if "login" not in config:
			raise ValueError("login object not in config")

		self.username = config["login"]["username"]
		password = config["login"]["password"]
		if len(self.username) < 1 or len(password) < 1:
			raise ValueError("username or password not provided")

		self.timeout = timeout
		self.last_sent = 0

		self.gmail = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		self.gmail.ehlo()
		self.gmail.login(self.username, password)

	def push(self, message=""):
		msg = MIMEMultipart()
		msg['From'] = self.username 
		msg['To'] = COMMASPACE.join(["trigger@applet.ifttt.com"])
		msg['Date'] = formatdate(localtime=True)
		msg['Subject'] = "#push"
		msg.attach(MIMEText(message))

		try:
			self.gmail.sendmail(self.username, ["trigger@applet.ifttt.com"], msg.as_string())
			return True
		except Exception as e:
			print("Trigger failed to send: {}".format(e))
			return False

	def on_recap(self, file):
		msg = MIMEMultipart()
		msg['From'] = self.username 
		msg['To'] = COMMASPACE.join(["aidan.dempster@gmail.com"])
		msg['Date'] = formatdate(localtime=True)
		msg['Subject'] = "Knock Recap"
		text = "You got a knock at {}".format(datetime.datetime.now().strftime("%H:%M"))
		msg.attach(MIMEText(text))

		with open(file, "rb") as fil:
			part = MIMEApplication(
				fil.read(),
				Name=basename(file)
			)
		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
		msg.attach(part)

		try:
			self.gmail.sendmail(self.username, ["aidan.dempster@gmail.com"], msg.as_string())
			return True
		except Exception as e:
			print("Trigger failed to send: {}".format(e))
			return False

	def close(self):
		self.gmail.close()
