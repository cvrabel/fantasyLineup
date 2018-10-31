#!/usr/bin/python3
# Chris Vrabel
# 10/19/18

# Script for Fantasy Basketball lineup setting.
# Login as League Manager and set every team's lineup.

import time
import sys
import os
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
from PlayerRow import PlayerRow

# teamNames = ['Scranton Stranglers', 'Nuclear Guam', 'Team Synchro', 'Team Droptop', 'Big Baller Brown', 'Chi Performing Artists', \
# 			 'Ithaca Splash Brothers', 'Wolf Wall', 'Tompkins CAT', 'Richmond Rogues', 'Boston Jellyfam', 'Luzern\'s Iron Chef']

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
	time.sleep(3)

def navigateToEditRosterPage(teamName, driver):
	dropdowns = driver.find_elements_by_class_name("dropdown__select")
	dropdowns[0].send_keys("Edit Rosters")
	dropdowns[1].send_keys(teamName)
	driver.find_element_by_link_text("Continue").click()
	time.sleep(5)

def extractPlayerFromRow(playerInfo, playerStats):
	playerName = findPlayerName(playerInfo)
	print(playerName)
	
	if playerName == "Empty" or playerName == "BLANK":
		return PlayerRow(playerName, None, None, None, None, None, None)

	positions = playerInfo.find_element_by_css_selector("span.playerinfo__playerpos.ttu").text.split(", ")
	hasGameToday = findIfHasGameToday(playerInfo)
	isInjured = findIfInjured(playerInfo)
	currentPosition = playerInfo.find_element_by_css_selector("div.jsx-2810852873.table--cell").text
	percentOwned = playerStats.find_element_by_css_selector("[title='Percent Owned']").text
	pr15 = playerStats.find_element_by_css_selector("[title^='Player Rating']").text
	return PlayerRow(playerName, currentPosition, positions, hasGameToday, isInjured, percentOwned, pr15)


def findPlayerName(playerInfo):
	try:
		playerName = playerInfo.find_element_by_css_selector("a.link.clr-link.pointer").text
		return playerName
	except:
		try:
			playerName = playerInfo.find_element_by_css_selector("div.jsx-2448508547.player-column__empty.flex.items-center.player-info").text
			return playerName
		except:
			return "BLANK"

def findIfHasGameToday(playerInfo):
	links = playerInfo.find_elements_by_css_selector("a.clr-link")
	for l in links:
		if "AM" in l.text or "PM" in l.text:
			return True
	return False

def findIfInjured(playerInfo):
	try:
		playerInfo.find_element_by_css_selector("span.jsx-425950755.playerinfo.playerinfo__injurystatus.injury-status_medium").text
		return True
	except:
		return False


def setLineup(driver):
	# daysList = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	# tomorrow = daysList[datetime.today().weekday() + 1]
	# thisWeek = driver.find_element_by_css_selector("div.Week.currentWeek")
	# tomorrowButton = thisWeek.find_element_by_xpath("//*[contains(text(), '{}')]".format(tomorrow))
	# tomorrowButton = thisWeek.find_elements_by_css_selector("div.jsx-1917748593.custom--day")[-1]
	# tomorrowButton.click()
	
	leftTable = driver.find_element_by_class_name('Table2__Table--fixed--left')
	rightTable = driver.find_element_by_class_name('Table2__table-scroller')

	playerInfoRows = leftTable.find_elements_by_class_name('Table2__tr--lg')
	playerStatsRows = rightTable.find_elements_by_class_name('Table2__tr--lg')

	playerList = []
	for i in range(0, len(playerInfoRows)):
		player = extractPlayerFromRow(playerInfoRows[i], playerStatsRows[i])
		playerList.append(player)

	indexOfBlank = 10
	for i in range(0, len(playerList)):
		if playerList[i].playerName == "BLANK":
			indexOfBlank = i 
			break

	nextIndexToMove = indexOfBlank + 1
	while(True):
		print("Index to Move: " + str(nextIndexToMove))
		prettyPrint(playerList)
		attempts = 0
		while attempts < 3:
			try:
				nextIndexToMove, playerList = moveBenchPlayer(leftTable, nextIndexToMove, playerList)
				break
			except Exception as e:
				attempts += 1
				print(e)
				
		if nextIndexToMove == -1 or nextIndexToMove > len(playerList):
			break


def moveBenchPlayer(leftTable, indexToMove, playerList):
	player = playerList[indexToMove]
	if player.currentPosition != "Bench":
		return -1, []

	if player.hasGameToday:
		rowToMove = leftTable.find_element_by_css_selector("[data-idx^='{}']".format(str(indexToMove)))
		time.sleep(1)
		moveButton = rowToMove.find_element_by_link_text("MOVE").click()
		time.sleep(1)
		hereButtons = leftTable.find_elements_by_link_text("HERE")
		return attemptToMoveToStart(indexToMove, hereButtons, playerList)

	return indexToMove+1, playerList

def attemptToMoveToStart(indexToMove, hereButtons, playerList):
	for button in hereButtons:
		hereIndex = int(button.find_element_by_xpath("../../../..").get_attribute("data-idx"))
		playerToMove = playerList[indexToMove]
		playerAtHereIndex = playerList[hereIndex]
		if playerToMove.currentPosition != "Bench":
			return -1, []
		elif playerAtHereIndex.playerName == "Empty":
			button.click()
			playerToMove.currentPosition = playerAtHereIndex.currentPosition
			playerList[hereIndex] = playerList[indexToMove]
			del playerList[indexToMove]
			return indexToMove, playerList
		elif playerAtHereIndex.hasGameToday == False:
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList
		elif len(playerAtHereIndex.positions) > len(playerToMove.positions):
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList
		elif playerAtHereIndex.percentOwned < playerToMove.percentOwned:
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList
	return indexToMove+1, playerList

def swapPositions(indexToMove, hereIndex, playerList):
	startingPosition = playerList[hereIndex].currentPosition
	playerList[hereIndex].setCurrentPosition(playerList[indexToMove].currentPosition)
	playerList[indexToMove].setCurrentPosition(startingPosition)
	playerList[hereIndex], playerList[indexToMove] = playerList[indexToMove], playerList[hereIndex]
	return playerList

def prettyPrint(playerList):
	print("Updated List")
	for player in playerList:
		print(player.playerName)
	print("list length: " + str(len(playerList)))
	print("-------")

def main(email, password, leagueId, teams):
	# driver = None
	# attempts = 0
	# while attempts < 5:
	# 	try:
	# 		driver = webdriver.Chrome(chrome_options=chrome_options)
	# 		break
	# 	except:
	# 		attempts += 1

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--window-size=1280x1696')
	chrome_options.add_argument('--user-data-dir=/tmp/user-data')
	chrome_options.add_argument('--hide-scrollbars')
	chrome_options.add_argument('--enable-logging')
	chrome_options.add_argument('--log-level=0')
	chrome_options.add_argument('--v=99')
	chrome_options.add_argument('--single-process')
	chrome_options.add_argument('--data-path=/tmp/data-path')
	chrome_options.add_argument('--ignore-certificate-errors')
	chrome_options.add_argument('--homedir=/tmp')
	chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
	chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
	chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"
	 
	driver = webdriver.Chrome(chrome_options=chrome_options)

	print("Webdriver opened chrome")
	url = "http://fantasy.espn.com/basketball/tools/lmrostermoves?leagueId={}".format(leagueId)
	driver.get(url)
	print("Connected to url")
	WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))
	time.sleep(5)
	# Login Page
	login(email, password, driver)
	
	for teamName in teams:
		print("Setting lineup for " + teamName)
		navigateToEditRosterPage(teamName, driver)
		setLineup(driver)
		print("Finished setting lineup for " + teamName)
		driver.get(url)

	driver.quit()
	print("Webdriver quit")

def lambda_handler(event, context):
	email = os.environ['email']
	password = os.environ['password']
	leagueId = os.environ['leagueId']
	teams = os.environ['teams'].split(",")
	main(email, password, leagueId, teams)

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument("-e", "--email", type=str, 
		help="ESPN login email", required=True)
	parser.add_argument("-p", "--password", type=str, 
		help="ESPN login password", required=True)
	parser.add_argument("-l", "--leagueId", type=str, 
		help="ESPN fantasy basketball leagueId", required=True)
	args = parser.parse_args()
	startTime = time.time()
	main(args.email, args.password, args.leagueId)
	print("--- %s seconds to execute ---" % (time.time() - startTime))
