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

def login(username, password, driver):
	# Login Page
	frames = driver.find_elements_by_xpath("(//iframe)")
	driver.switch_to_frame(frames[1])
	driver.find_element_by_xpath("(//input)[1]").send_keys(username)	
	driver.find_element_by_xpath("(//input)[2]").send_keys(password)
	driver.find_element_by_xpath("//button[2]").click()
	driver.switch_to_default_content()
	time.sleep(3)

def playActives(driver):
	playerRowList = driver.find_elements_by_class_name("pncPlayerRow")
	gameStatusList = driver.find_elements_by_class_name("gameStatusDiv")
	numPlayers = len(playerRowList) - 1

	for n in range(numPlayers-6, numPlayers):
		pncSlot = "pncSlot_" + str(n)
		if playerRowList[n].find_element_by_id(pncSlot).text == "Bench":
			driver.find_elements_by_class_name("pncButtonMove")[n].click()
			time.sleep(1)
			hereButtonList = driver.find_elements_by_class_name("pncButtonHere")
			for m in range(len(hereButtonList)):
				idString = hereButtonList[m].get_attribute("id")
				playerNumber = idString[idString.index("_")+1:]
				print(playerNumber)

				if m == len(hereButtonList) - 1:
					time.sleep(1)
					print(driver.find_element_by_class_name("pncButtonMoveSelected").get_property("display"))
			time.sleep(1)

	driver.find_element_by_id("pncSaveRoster0").click()

def setLineup(username, password):
	chrome_options = webdriver.ChromeOptions()
	# chrome_options.add_argument('headless')
	driver = webdriver.Chrome(chrome_options=chrome_options)
	print("Webdriver opened chrome")

	try:
		driver.get('http://games.espn.com/fba/signin?redir=http%3A%2F%2Fgames.espn.com%2Ffba%2Fclubhouse%3FteamId%3D1%26leagueId%3D163326%26seasonId%3D2018')
		print("Connected to url")
		WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))
		# driver.save_screenshot("screenshot.png")

		login(username, password, driver)

		# Team Page
		playActives(driver)

	finally:
		time.sleep(1)
		driver.quit()
		print("Webdriver closed")


if __name__ == '__main__':
	setLineup(sys.argv[1], sys.argv[2])