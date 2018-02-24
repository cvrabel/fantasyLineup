#!/usr/bin/python3
# Chris Vrabel
# 2/17/18

# Script to log into ESPN Fantasy Basketball team page 
# then set your lineup.

import time
import boto3
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
	numPlayers = len(playerRowList) - 1

	for n in range(0, numPlayers):
		pncSlot = "pncSlot_" + str(n)
		gameStatusList = driver.find_elements_by_class_name("gameStatusDiv")
		print(playerRowList[n].get_attribute("id"))
		if playerRowList[n].find_element_by_id(pncSlot).text == "Bench" and len(gameStatusList[n].text) != 0:
			# Find button of player to move, and get id of that button
			moveButton = driver.find_elements_by_class_name("pncButtonMove")[n]
			moveButtonId = moveButton.get_attribute("id")
			moveButtonNumber = moveButtonId[moveButtonId.index("_")+1:]
			moveButton.click()

			time.sleep(1)

			# Get all buttons where the player can be moved to
			hereButtonList = driver.find_elements_by_class_name("pncButtonHere")

			for m in range(len(hereButtonList)):
				# Get id of the destination
				idString = hereButtonList[m].get_attribute("id")
				playerNumber = int(idString[idString.index("_")+1:])

				# Find game status of that player today. If no game then move player here
				if len(gameStatusList[playerNumber].text) == 0:
					hereButtonList[m].click()
					break

				if m == len(hereButtonList) - 1:
					driver.find_element_by_id("pncButtonMoveSelected_" + moveButtonNumber).click()

			time.sleep(1)

	driver.find_element_by_id("pncSaveRoster0").click()

def loginThenSetLineup(item):
	try:
		username = item['email']
		password = item['password']
		leagueId = item['leagueId']
		teamId = item['teamId']
		seasonId = item['seasonId']

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('headless')
		driver = webdriver.Chrome(chrome_options=chrome_options)
		print("Webdriver opened chrome")

		url = "http://games.espn.com/fba/signin?redir=http%3A%2F%2Fgames.espn.com%2Ffba%2Fclubhouse%3FteamId%3D{}%26leagueId%3D{}%26seasonId%3D{}".format(teamId, leagueId, seasonId)
		# driver.get('http://games.espn.com/fba/signin?redir=http%3A%2F%2Fgames.espn.com%2Ffba%2Fclubhouse%3FteamId%3D1%26leagueId%3D163326%26seasonId%3D2018')
		driver.get(url)
		print("Connected to url")
		WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))

		# Login Page
		login(username, password, driver)

		# Team Page
		playActives(driver)

	finally:
		driver.quit()
		print("Webdriver quit")

def setLineupForEachItem(items):
	for item in items:
		for x in range(5):
			try:
				loginThenSetLineup(item)
			except:
				continue
			print("Set lineup for {}".format(item['email']))
			break
	print("Finished entire table")

if __name__ == '__main__':
	dynamodb = boto3.resource('dynamodb')
	userInfoTable = dynamodb.Table('UserInfo')
	response = userInfoTable.scan()
	setLineupForEachItem(response['Items'])
