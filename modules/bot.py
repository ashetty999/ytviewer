import os
import time
import random
import signal
import logging
from pathlib import Path
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome,ChromeOptions,Firefox,FirefoxOptions

class Bot(object):
	def __init__(self):
		self.driver=None
		self.running=True
	def run(self,urls,browser,proxies,referers,user_agents,duration,executable_path,extension_paths):
		signal.signal(signal.SIGINT,self.quit)
		logging.basicConfig(level=logging.CRITICAL)
		while self.running:
			try:
				proxy=proxies.get()
				seleniumwire_options={
					'proxy':{
						'http':f'http://{proxy}',
						'https':f'https://{proxy}',
						'no_proxy':'localhost,127.0.0.1'
					},
					'connection_timeout':None,
					'verify_ssl':False
				}
				user_agent=user_agents.get()
				if browser=='chrome':
					options=ChromeOptions()
					options.add_argument('--no-sandbox')
					options.add_argument('--mute-audio')
					options.add_argument('--disable-gpu')
					options.add_argument('--disable-dev-shm-usage')
					options.add_argument(f'--user-agent={user_agent}')
					options.add_experimental_option('excludeSwitches',['enable-logging'])
					WebDriver=Chrome
				else:
					options=FirefoxOptions()
					options.add_argument('--headless')
					options.preferences.update({
						'media.volume_scale':'0.0',
						'media.peerconnection.enabled':False,
						'general.useragent.override':user_agent
					})
					WebDriver=Firefox
				self.driver=WebDriver(
					executable_path=executable_path,
					options=options,
					service_log_path=os.devnull,
					seleniumwire_options=seleniumwire_options
				)
				self.driver.minimize_window()
				self.driver.header_overrides={
					'Referer':referers.get()
				}
				self.driver.set_page_load_timeout(60)
				try:
					self.driver.get(urls.get())
				except:
					pass
				finally:
					if self.driver.title.endswith('YouTube'):
						try:
							WebDriverWait(self.driver,3).until(EC.element_to_be_clickable((By.CLASS_NAME,'ytp-large-play-button'))).click()
						except:
							pass
						finally:
							if duration:
								time.sleep(duration)
							else:
								video=WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.CLASS_NAME,'html5-main-video')))
								video_duration=self.driver.execute_script('return arguments[0].getDuration()',video)
								time.sleep(float(video_duration)*random.uniform(0.35,0.85))
			except:
				pass
			finally:
				self.close()
	def close(self):
		try:
			self.driver.quit()
		except:
			pass
	def quit(self,*args):
		self.running=False
		self.close()
