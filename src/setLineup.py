#!/usr/bin/python3
# Chris Vrabel
# 10/19/18

# Lambda Script for Fantasy Basketball lineup setting.
# Login as League Manager and set specified team's lineup.

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

def main(email, password, leagueId, teams, hasGamesPlayedLimit):
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

	daysList = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	today = daysList[datetime.today().weekday()]
	gamesRemainingDict = {}
	if hasGamesPlayedLimit == "True" and (today == 'Sat' or today == 'Sun'):   
		url = "http://fantasy.espn.com/basketball/league/scoreboard?leagueId={}".format(leagueId)
		driver.get(url)
		print("Connected to url")
		WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))
		time.sleep(1)
		# Login Page
		login(email, password, driver)
		gamesRemainingDict = findGamesRemainingForTeams(driver, url)
		print(gamesRemainingDict)

	else:
		url = "http://fantasy.espn.com/basketball/tools/lmrostermoves?leagueId={}".format(leagueId)
		driver.get(url)
		print("Connected to url")
		WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))
		time.sleep(1)
		# Login Page
		login(email, password, driver)

	
	url = "http://fantasy.espn.com/basketball/tools/lmrostermoves?leagueId={}".format(leagueId)
	for teamName in teams:
		driver.get(url)
		print("Setting lineup for " + teamName)
		navigateToEditRosterPage(teamName, driver)
		teamGamesRemaining = 20
		try:
			teamGamesRemaining = gamesRemainingDict[teamName]
		except:
			print("Games Remaining Dictionary is empty.")
		setLineup(driver, teamGamesRemaining)
		print("Finished setting lineup for " + teamName)

	driver.quit()
	print("Webdriver quit")
	return "Lambda finished."

def login(username, password, driver):
	# Login Page
	driver.switch_to_frame("disneyid-iframe")
	emailInput = driver.find_element_by_xpath("(//input)[1]")
	passwordInput = driver.find_element_by_xpath("(//input)[2]")

	emailInput.send_keys(username)	
	passwordInput.send_keys(password)
	passwordInput.send_keys(Keys.RETURN)
	
	driver.switch_to_default_content()
	time.sleep(3)

def findGamesRemainingForTeams(driver, url):
	boxScoreButtons = driver.find_elements_by_link_text("BOX SCORE")
	print(len(boxScoreButtons))
	teamGamesRemaining = {}
	for buttonNum in range(len(boxScoreButtons)):
		print("Navigating to box score " + str(buttonNum))
		boxScoreButtons[buttonNum].click()
		time.sleep(2)
		dictFromBoxScore = findGamesPlayedFromBoxScore(driver)
		teamGamesRemaining.update(dictFromBoxScore)
		driver.get(url)
		time.sleep(2)
		boxScoreButtons = driver.find_elements_by_link_text("BOX SCORE")
	return teamGamesRemaining

def findGamesPlayedFromBoxScore(driver):
	teamNames = driver.find_elements_by_css_selector("span.teamName.truncate")
	teamLimitDivs = driver.find_elements_by_css_selector("div.team-limits")
	teamGamesRemaining = {}
	for i in range(2):
		gamesPlayedSplitBySpace = teamLimitDivs[i].find_element_by_xpath("//td[contains(text(),'Cur/Max')]").text.split(" ")
		gamesFraction = gamesPlayedSplitBySpace[2].split("/")
		gamesRemaining = int(gamesFraction[1]) - int(gamesFraction[0])
		teamGamesRemaining.update({teamNames[i].text: gamesRemaining})
	return teamGamesRemaining

def navigateToEditRosterPage(teamName, driver):
	dropdowns = driver.find_elements_by_class_name("dropdown__select")
	dropdowns[0].send_keys("Edit Roster")
	dropdowns[1].send_keys(teamName)
	driver.find_element_by_link_text("Continue").click()
	time.sleep(5)

def setLineup(driver, gamesRemaining):
	# daysList = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	# tomorrow = daysList[datetime.today().weekday() + 1]
	thisWeek = driver.find_element_by_css_selector("div.Week.currentWeek")
	# tomorrowButton = thisWeek.find_element_by_xpath("//*[contains(text(), '{}')]".format(tomorrow))
	tomorrowButton = thisWeek.find_elements_by_css_selector("div.jsx-1917748593.custom--day")[-1]
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
	numStarting = 0
	for i in range(0, len(playerList)):
		if playerList[i].hasGameToday == True:
			numStarting = numStarting + 1
		if playerList[i].playerName == "BLANK":
			indexOfBlank = i 
			break

	gamesRemaining = gamesRemaining - numStarting
	if (numStarting >= indexOfBlank and gamesRemaining >= 0) or gamesRemaining == 0:
		print("Lineup has {} games, and now have {} gamesRemaining. Nothing to change.".format(numStarting, gamesRemaining))
		return

	nextIndexToMove = indexOfBlank + 1
	while(True):
		prettyPrint(playerList, str(nextIndexToMove))
		attempts = 0
		while attempts < 3:
			try:
				if gamesRemaining > 0:
					nextIndexToMove, playerList, gamesRemaining = moveBenchPlayer(leftTable, nextIndexToMove, playerList, gamesRemaining)
				elif gamesRemaining == 0:
					print("Zero games remaining. Don't move to starting lineup.")
				elif gamesRemaining < 0:
					print("Too many starting, will go over limit. Moving starting players to bench.")
					nextIndexToMove, playerList, gamesRemaining = movePlayersOutOfStartingLineup(leftTable, playerList, abs(gamesRemaining))
				break
			except Exception as e:
				attempts += 1
				print(e)
				
		if nextIndexToMove == -1 or nextIndexToMove >= len(playerList):
			break

	emptyStartingSpots, gamesOnBench = findEmptyStartingSpotsAndGamesOnBench(playerList, indexOfBlank)
	
	if len(emptyStartingSpots) > 0 and len(gamesOnBench) > 0:
		print("Empty starting spots with games on bench. Attempting to fix.")
		leftTable = driver.find_element_by_class_name('Table2__Table--fixed--left')
		attemptToMoveToStartWithReArrange(leftTable, emptyStartingSpots, gamesOnBench, playerList, indexOfBlank)



def extractPlayerFromRow(playerInfo, playerStats):
	currentPosition = playerInfo.find_element_by_css_selector("div.jsx-2810852873.table--cell").text
	playerName = findPlayerName(playerInfo)
	print(currentPosition + ": " + playerName)

	if playerName == "Empty" or playerName == "BLANK":
		return PlayerRow(playerName, currentPosition, None, False, None, None, None)

	positions = playerInfo.find_element_by_css_selector("span.playerinfo__playerpos.ttu").text.split(", ")
	hasGameToday = findIfHasGameToday(playerInfo)
	isInjured = findIfInjured(playerInfo)
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


def movePlayersOutOfStartingLineup(leftTable, playerList, indexOfBlank, numToMove):
	indicesToRemove = {}
	# Finding numToMove starting players lowest percent owns
	for i in range(indexOfBlank):
		if playerList[i].hasGameToday == False:
			continue

		currentPercentOwned = playerList[i].percentOwned
		if len(indicesToRemove) < numToMove:
			indicesToRemove.update({i: currentPercentOwned })
		else:
			for key,value in indicesToRemove.items():
				if value < currentPercentOwned:
					del indicesToRemove[key]
					indicesToRemove.update({i: currentPercentOwned})
					break

	print("Indices to remove.")
	print(indicesToRemove)
	# Move the indices in indicesToRemove to bench
	for key,value in indicesToRemove.items():
		time.sleep(1)
		rowToMove = leftTable.find_element_by_css_selector("[data-idx^='{}']".format(str(key)))
		time.sleep(1)
		moveButton = rowToMove.find_element_by_link_text("MOVE").click()
		time.sleep(1)
		hereButtons = leftTable.find_elements_by_link_text("HERE")
		hereButtons[-1].click()
		numToMove = numToMove - 1

	return -1, playerList, numToMove



def attemptToMoveToStartWithReArrange(leftTable, emptyStartingSpots, gamesOnBench, playerList, indexOfBlank):
	numEmptyStartingSpots = len(emptyStartingSpots)
	numGamesOnBench = len(gamesOnBench)
	for i in range(indexOfBlank):
		for e in range(len(emptyStartingSpots)):
			for g in range(len(gamesOnBench)):
				currentSpot = playerList[i]
				emptyStart = playerList[emptyStartingSpots[e]]
				gameOnBench = playerList[gamesOnBench[g]]
				if canMoveToSpot(currentSpot, emptyStart) and canMoveToSpot(gameOnBench, currentSpot):
					print("Can move currentSpot: {} to emptyStart: {}. Can move gameOnBench: {} to currentSpot: {}" \
						.format(str(i), str(emptyStartingSpots[e]), str(gamesOnBench[g]), str(i)))
					playerList = moveToSpecificIndex(leftTable, i, emptyStartingSpots[e], playerList)
					prettyPrint(playerList, i)
					playerList = moveToSpecificIndex(leftTable, gamesOnBench[g], i, playerList)
					prettyPrint(playerList, gamesOnBench[g])
					numEmptyStartingSpots = numEmptyStartingSpots - 1
					numGamesOnBench = numGamesOnBench - 1
				if numEmptyStartingSpots == 0 or numGamesOnBench == 0:
					print("Done rearranging.")
					return


def moveToSpecificIndex(leftTable, fromSpot, toSpot, playerList):
	rowToMove = leftTable.find_element_by_css_selector("[data-idx^='{}']".format(str(fromSpot)))
	time.sleep(1)
	moveButton = rowToMove.find_element_by_link_text("MOVE").click()
	time.sleep(1)
	hereButtons = leftTable.find_elements_by_link_text("HERE")
	for button in hereButtons:
		hereIndex = int(button.find_element_by_xpath("../../../..").get_attribute("data-idx"))
		playerAtHereIndex = playerList[hereIndex]
		if hereIndex == toSpot:
			print("Rearranging from index {} to index {}".format(fromSpot, toSpot))
			button.click()
			return swapPositions(fromSpot, hereIndex, playerList)

	# Did not get to move so click move again
	rowToMove.find_element_by_link_text("MOVE").click()
	return playerList


def canMoveToSpot(fromSpot, toSpot):
	fromPositions = fromSpot.positions
	toPosition = toSpot.currentPosition
	if fromPositions is None:
		return False
	elif toPosition == "UTIL":
		return True
	elif toPosition == "PG":
		return findIfPositionsContains(fromPositions, "PG")
	elif toPosition == "SG":
		return findIfPositionsContains(fromPositions, "SG")
	elif toPosition == "SF":
		return findIfPositionsContains(fromPositions, "SF")
	elif toPosition == "PF":
		return findIfPositionsContains(fromPositions, "PF")
	elif toPosition == "C":
		return findIfPositionsContains(fromPositions, "C")
	elif toPosition == "G":
		return findIfPositionsContains(fromPositions, "G")
	elif toPosition == "F":
		return findIfPositionsContains(fromPositions, "F")

def findIfPositionsContains(fromPositions, position):
	for fromPos in fromPositions:
		if position in fromPos:
			return True
	return False

def findEmptyStartingSpotsAndGamesOnBench(playerList, indexOfBlank):
	emptyStartingSpots = []
	gamesOnBench = []
	for i in reversed(range(len(playerList))):
		if i < indexOfBlank and playerList[i].hasGameToday == False:
			print("Found empty starting spot.")
			emptyStartingSpots.append(i)
		elif i > indexOfBlank and playerList[i].hasGameToday == True and playerList[i].currentPosition == "Bench":
			print("Found games on bench.")
			gamesOnBench.append(i)
	return emptyStartingSpots, gamesOnBench



def moveBenchPlayer(leftTable, indexToMove, playerList, gamesRemaining):
	player = playerList[indexToMove]
	if player.currentPosition != "Bench":
		print("PlayerToMove not on bench.  Ignoring")
		return -1, playerList, gamesRemaining

	if player.hasGameToday:
		rowToMove = leftTable.find_element_by_css_selector("[data-idx^='{}']".format(str(indexToMove)))
		time.sleep(1)
		moveButton = rowToMove.find_element_by_link_text("MOVE").click()
		time.sleep(1)
		hereButtons = leftTable.find_elements_by_link_text("HERE")
		return attemptToMoveToStart(indexToMove, hereButtons, playerList, leftTable, gamesRemaining)

	print("PlayerToMove has no game today.  Move to next index.")
	return indexToMove+1, playerList, gamesRemaining

def attemptToMoveToStart(indexToMove, hereButtons, playerList, leftTable, gamesRemaining):
	for button in hereButtons:
		hereIndex = int(button.find_element_by_xpath("../../../..").get_attribute("data-idx"))
		playerToMove = playerList[indexToMove]
		playerAtHereIndex = playerList[hereIndex]
		if playerToMove.currentPosition != "Bench":
			print("PlayerToMove not on bench.  Ignoring")
			return -1, playerList, gamesRemaining
		elif playerAtHereIndex.playerName == "Empty":
			print("Starting position is empty. Moving here.")
			button.click()
			playerToMove.currentPosition = playerAtHereIndex.currentPosition
			playerList[hereIndex] = playerList[indexToMove]
			del playerList[indexToMove]
			return indexToMove, playerList, gamesRemaining-1
		elif playerAtHereIndex.hasGameToday == False:
			print("Starting position has no game today. Moving here.")
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList, gamesRemaining-1
		elif len(playerAtHereIndex.positions) > len(playerToMove.positions):
			print(playerAtHereIndex.positions)
			print(playerToMove.positions)	
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList, gamesRemaining-1
		elif len(playerAtHereIndex.positions) < len(playerToMove.positions):
			print("PlayerToMove has less positions than starter. Continue to next button.")
			continue
		elif playerAtHereIndex.percentOwned < playerToMove.percentOwned:
			print(playerAtHereIndex.percentOwned)
			print(playerToMove.percentOwned)
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList, gamesRemaining-1
		else:
			print("Can't more here. Continue to next button.")
			continue
	print("No place to move. Go to next index.")
	rowToMove = leftTable.find_element_by_css_selector("[data-idx^='{}']".format(str(indexToMove)))
	time.sleep(1)
	rowToMove.find_element_by_link_text("MOVE").click()
	return indexToMove+1, playerList, gamesRemaining

def swapPositions(indexToMove, hereIndex, playerList):
	startingPosition = playerList[hereIndex].currentPosition
	playerList[hereIndex].setCurrentPosition(playerList[indexToMove].currentPosition)
	playerList[indexToMove].setCurrentPosition(startingPosition)
	playerList[hereIndex], playerList[indexToMove] = playerList[indexToMove], playerList[hereIndex]
	return playerList

def prettyPrint(playerList, nextIndexToMove):
	print("-----------------")
	print("Index to Move: " + str(nextIndexToMove))
	for i in range(0, len(playerList)):
		player = playerList[i]
		print(player.currentPosition + "(" + str(i) + "): " + player.playerName)

def lambda_handler(event, context):
	email = os.environ['email']
	password = os.environ['password']
	leagueId = os.environ['leagueId']
	teams = os.environ['teams'].split(",")
	hasGamesPlayedLimit = os.environ['hasGamesPlayedLimit']
	return main(email, password, leagueId, teams, hasGamesPlayedLimit)

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument("-e", "--email", type=str, 
		help="ESPN login email", required=True)
	parser.add_argument("-p", "--password", type=str, 
		help="ESPN login password", required=True)
	parser.add_argument("-l", "--leagueId", type=str, 
		help="ESPN fantasy basketball leagueId", required=True)
	parser.add_argument
	args = parser.parse_args()
	startTime = time.time()
	main(args.email, args.password, args.leagueId, "Chi Performing Artists")
	print("--- %s seconds to execute ---" % (time.time() - startTime))
