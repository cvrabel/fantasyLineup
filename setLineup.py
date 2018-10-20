#!/usr/bin/python3
# Chris Vrabel
# 10/19/18

# Script for Fantasy Basketball lineup setting.
# Login as League Manager and set every team's lineup.

import time
import boto3
import sys
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime

teamNames = ['Scranton Stranglers', 'Nuclear Guam', 'Team Synchro', 'Team Droptop', 'Big Baller Brown', 'Chi Performing Artists', \
			 'Ithaca Splash Brothers', 'Wolf Wall', 'Tompkins CAT', 'Richmond Rogues', 'Boston Jellyfam', 'Luzern\'s Iron Chef']

def login(username, password, driver):
	# Login Page
	driver.switch_to_frame("disneyid-iframe")
	emailInput = driver.find_element_by_xpath("(//input)[1]")
	passwordInput = driver.find_element_by_xpath("(//input)[2]")

	emailInput.send_keys(username)	
	passwordInput.send_keys(password)
	passwordInput.send_keys(Keys.RETURN)
	
	# driver.find_element_by_xpath("//button[1]").click()
	driver.switch_to_default_content()
	time.sleep(2)

def navigateToEditRosterPage(teamName, driver):
	dropdowns = driver.find_elements_by_class_name("dropdown__select")
	dropdowns[0].send_keys("Edit Rosters")
	dropdowns[1].send_keys(teamName)
	driver.find_element_by_link_text("Continue").click()
	time.sleep(3)

def setLineup(driver):
	daysList = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	tomorrow = daysList[datetime.today().weekday() + 1]

	driver.find_element_by_xpath("//*[contains(text(), '{}')]".format(tomorrow)).click()
	opponents = driver.find_elements_by_xpath("//*[@title='Opponent']")
	for t in opponents:
		print(t.text)
	
	numGamesToday = len([k for k in opponents if ('OPP' not in k.text and '--' not in k.text)])
	print(numGamesToday)

	# playerRowList = driver.find_elements_by_class_name("pncPlayerRow")
	# numPlayers = len(playerRowList) - 1

	# for n in range(0, numPlayers):
	# 	pncSlot = "pncSlot_" + str(n)
	# 	gameStatusList = driver.find_elements_by_class_name("gameStatusDiv")
	# 	print(playerRowList[n].get_attribute("id"))
	# 	if playerRowList[n].find_element_by_id(pncSlot).text == "Bench" and len(gameStatusList[n].text) != 0:
	# 		# Find button of player to move, and get id of that button
	# 		moveButton = driver.find_elements_by_class_name("pncButtonMove")[n]
	# 		moveButtonId = moveButton.get_attribute("id")
	# 		moveButtonNumber = moveButtonId[moveButtonId.index("_")+1:]
	# 		moveButton.click()

	# 		time.sleep(1)

	# 		# Get all buttons where the player can be moved to
	# 		hereButtonList = driver.find_elements_by_class_name("pncButtonHere")

	# 		for m in range(len(hereButtonList)):
	# 			# Get id of the destination
	# 			idString = hereButtonList[m].get_attribute("id")
	# 			playerNumber = int(idString[idString.index("_")+1:])

	# 			# Find game status of that player today. If no game then move player here
	# 			if len(gameStatusList[playerNumber].text) == 0:
	# 				hereButtonList[m].click()
	# 				break

	# 			if m == len(hereButtonList) - 1:
	# 				driver.find_element_by_id("pncButtonMoveSelected_" + moveButtonNumber).click()

	# 		time.sleep(1)

	# driver.find_element_by_id("pncSaveRoster0").click()

def main(email, password, leagueId):
	try:
		chrome_options = webdriver.ChromeOptions()
		# chrome_options.add_argument('headless')
		driver = webdriver.Chrome(chrome_options=chrome_options)
		print("Webdriver opened chrome")

		url = "http://fantasy.espn.com/basketball/tools/lmrostermoves?leagueId={}".format(leagueId)
		driver.get(url)
		print("Connected to url")
		WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))
		time.sleep(5)
		# Login Page
		login(email, password, driver)
		
		for teamName in teamNames:
			print("Setting lineup for " + teamName)
			navigateToEditRosterPage(teamName, driver)
			setLineup(driver)
			driver.get(url)

	finally:
		driver.quit()
		print("Webdriver quit")

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument("-e", "--email", type=str, 
		help="ESPN login email", required=True)
	parser.add_argument("-p", "--password", type=str, 
		help="ESPN login password", required=True)
	parser.add_argument("-l", "--leagueId", type=str, 
		help="ESPN fantasy basketball leagueId", required=True)
	args = parser.parse_args()
	main(args.email, args.password, args.leagueId)
