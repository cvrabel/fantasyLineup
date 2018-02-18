# Chris Vrabel
# 2/17/18

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys

def setLineup(username, password):
	print(username)
	print(password)


	chrome_options = webdriver.ChromeOptions()
	# chrome_options.add_argument('headless')
	driver = webdriver.Chrome(chrome_options=chrome_options)
	# driver.set_window_size(1920, 1080)
	# driver.maximize_window()
	print("Webdriver opened chrome")
	try:
		driver.get('http://games.espn.com/fba/signin?redir=http%3A%2F%2Fgames.espn.com%2Ffba%2Fclubhouse%3FteamId%3D1%26leagueId%3D163326%26seasonId%3D2018')
		print("Connected to url")
		WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))
		driver.save_screenshot("screenshot.png")

		frames = driver.find_elements_by_xpath("(//iframe)")
		driver.switch_to_frame(frames[1])

		driver.find_element_by_xpath("(//input)[1]").send_keys(username)	
		driver.find_element_by_xpath("(//input)[2]").send_keys(password)

		# time.sleep(8)
		driver.find_element_by_xpath("//button[2]").click()
		driver.switch_to_default_content()
		time.sleep(4)

		print(driver.find_elements_by_class_name("gameStatusDiv"))

		# # hover to Fantasy Basketball to display the hidden dropdown menu 
		# teams = driver.find_element_by_xpath("//li[@class = 'Navitem Navitem-main Navitem-fantasy Va-top Fl-start Topstart']")
		# hov = ActionChains(driver).move_to_element(teams)
		# hov.perform()
		# time.sleep(1)

		# driver.find_element_by_xpath("//a[text() = '"+ teamname +"']").click()
		# time.sleep(2)

		# for x in range(0, days):

		# 	driver.find_element_by_xpath("//a[text() = 'Start Active Players']").click()
		# 	time.sleep(2)
		# 	date_text = driver.find_element_by_xpath("//span[@class='flyout-title']").text
		# 	print("Starting active players for: " + date_text)
		# 	driver.find_element_by_xpath("//a[contains(@class, 'Js-next')]").click()
		# 	time.sleep(2)
		print("here")
	finally:
		driver.quit()
		print("Webdriver closed")


if __name__ == '__main__':
	setLineup(sys.argv[1], sys.argv[2])