#!/usr/bin/python3
# Chris Vrabel
# 10/19/18

# Lambda Script for Fantasy Basketball lineup setting.
# Login as League Manager and set specified team's lineup.

import time
import sys
import os
import benchStarters as bencher
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

"""
The main method.
1)	Opens headless chrome.
2)	Logs in using given credentials.
3)  Sets lineup for each team in list
"""
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
	chrome_options.add_argument('--incognito')
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
	time.sleep(1)
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
	return "Lambda finished."

"""
Function to log into espn using given credentials.
"""
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

"""
From the league manager page, uses teamName and navigates to the 
edit roster page for that team.
"""
def navigateToEditRosterPage(teamName, driver):
	dropdowns = driver.find_elements_by_class_name("dropdown__select")
	dropdowns[0].send_keys("Edit Roster")
	dropdowns[1].send_keys(teamName)
	driver.find_element_by_link_text("Continue").click()
	time.sleep(5)

"""
Method which handles the general logic of setting lineup for a team.
1)	Extracts player info from each row on the roster
2)  Tries moving bench players to starting lineup.
3)	If there are still opening starts and games on bench, attempt to fix that.
"""
def setLineup(driver):
	# daysList = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	# tomorrow = daysList[datetime.today().weekday() + 1]
	# thisWeek = driver.find_element_by_css_selector("div.Week.currentWeek")
	# tomorrowButton = thisWeek.find_element_by_xpath("//*[contains(text(), '{}')]".format(tomorrow))
	# tomorrowButton = thisWeek.find_elements_by_css_selector("div.jsx-1917748593.custom--day")[-1].click()
	
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

	nextIndexToMove = indexOfBlank + 1
	while(True):
		prettyPrint(playerList)
		print("Attempting to move {}".format(nextIndexToMove))
		attempts = 0
		while attempts < 3:
			try:
				nextIndexToMove, playerList = moveBenchPlayer(leftTable, nextIndexToMove, playerList)
				break
			except Exception as e:
				attempts += 1
				print(e)
				
		if nextIndexToMove == -1 or nextIndexToMove >= len(playerList):
			break

	emptyStartingSpots, gamesOnBench = findEmptyStartingSpotsAndGamesOnBench(playerList, indexOfBlank)
	
	if len(emptyStartingSpots) > 0 and len(gamesOnBench) > 0:
		print("{} empty starting spots with {} games on bench. Attempting to fix.".format(len(emptyStartingSpots), len(gamesOnBench)))
		leftTable = driver.find_element_by_class_name('Table2__Table--fixed--left')
		attemptToMoveToStartWithReArrange(leftTable, emptyStartingSpots, gamesOnBench, playerList, indexOfBlank)


"""
Create a PlayerRow object from this row.  
Extract important info like playerName, positions, hasGameToday, etc... (See PlayerRow class)
"""
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

"""
Find the player's name from this webelement. Fallback logic to determine if empty slot or blank row.
"""
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

"""
Find if player has a game today from this webelement.
"""
def findIfHasGameToday(playerInfo):
	links = playerInfo.find_elements_by_css_selector("a.clr-link")
	for l in links:
		if "AM" in l.text or "PM" in l.text:
			return True
	return False

"""
Find if player is injured from this webelement.
"""
def findIfInjured(playerInfo):
	try:
		playerInfo.find_element_by_css_selector("span.jsx-425950755.playerinfo.playerinfo__injurystatus.injury-status_medium").text
		return True
	except:
		return False

"""
Logic to fix corner case where a game is on bench and there is an open spot.
Finds a starter who the bench player can replace, and if starter can move to the empty spot.
"""
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
					playerList = moveToSpecificIndex(leftTable, gamesOnBench[g], i, playerList)
					prettyPrint(playerList)
					numEmptyStartingSpots = numEmptyStartingSpots - 1
					numGamesOnBench = numGamesOnBench - 1
				if numEmptyStartingSpots == 0 or numGamesOnBench == 0:
					print("Done rearranging.")
					return

"""
Used only by attemptToMoveToStartWithReArrange().  This is so we can insert the player to a specific spot,
rather than the usual logic where we simply loop top to bottom and find a fit.
"""
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

"""
Return if player can move to spot (if player is elibible for that position)
"""
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

"""
Return true if one of the player's positions is elibile for this position.
"""
def findIfPositionsContains(fromPositions, position):
	for fromPos in fromPositions:
		if position in fromPos:
			return True
	return False

"""
Return the number of empty starting spots and number of games on the bench.
"""
def findEmptyStartingSpotsAndGamesOnBench(playerList, indexOfBlank):
	emptyStartingSpots = []
	gamesOnBench = []
	for i in reversed(range(len(playerList))):
		if i < indexOfBlank and playerList[i].hasGameToday == False:
			emptyStartingSpots.append(i)
		elif i > indexOfBlank and playerList[i].hasGameToday == True and playerList[i].currentPosition == "Bench":
			gamesOnBench.append(i)
	return emptyStartingSpots, gamesOnBench

"""
Move bench player to starting spot if has a game today.
Click on this player's button, then attempt to move the player 
to each of his possible here buttons (from top to bottom).
"""
def moveBenchPlayer(leftTable, indexToMove, playerList):
	player = playerList[indexToMove]
	if player.currentPosition != "Bench":
		print("PlayerToMove not on bench.  Ignoring")
		return -1, playerList

	if player.hasGameToday:
		rowToMove = leftTable.find_element_by_css_selector("[data-idx^='{}']".format(str(indexToMove)))
		time.sleep(1)
		moveButton = rowToMove.find_element_by_link_text("MOVE").click()
		time.sleep(1)
		hereButtons = leftTable.find_elements_by_link_text("HERE")
		return attemptToMoveToStart(indexToMove, hereButtons, playerList, leftTable)

	print("PlayerToMove has no game today.  Move to next index.")
	return indexToMove+1, playerList

"""
Iterate through a bench player's possible starting spots and move to first place permitted by logic.
Can move to spot if:
	- The starting spot is empty
	- The starting spot has no game today
	- The starting spot is a UTIL spot and is less owned
	- The starting spot has more positions 
	- The starting spot has equal num positions but is less owned
If we cannot move to any of these spots, return indexToMove+1, indicating to try next guy on bench.
"""
def attemptToMoveToStart(indexToMove, hereButtons, playerList, leftTable):
	for button in hereButtons:
		hereIndex = int(button.find_element_by_xpath("../../../..").get_attribute("data-idx"))
		playerToMove = playerList[indexToMove]
		playerAtHereIndex = playerList[hereIndex]
		if playerToMove.currentPosition != "Bench":
			print("PlayerToMove not on bench.  Ignoring")
			return -1, playerList
		elif playerAtHereIndex.playerName == "Empty":
			print("Starting position at {} is empty. Moving here.".format(hereIndex))
			button.click()
			playerToMove.currentPosition = playerAtHereIndex.currentPosition
			playerList[hereIndex] = playerList[indexToMove]
			del playerList[indexToMove]
			return indexToMove, playerList
		elif playerAtHereIndex.hasGameToday == False:
			print("Starting position at {} has no game today. Moving here.".format(hereIndex))
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList
		elif playerAtHereIndex.currentPosition == 'UTIL' and playerAtHereIndex.percentOwned < playerToMove.percentOwned:
			print("PlayerToMove has greater own percentage than starter in UTIL spot. Moving to index {}".format(hereIndex))
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList
		elif len(playerAtHereIndex.positions) > len(playerToMove.positions):
			print("PlayerToMove has less positions than starter with game at {}. Moving here.".format(hereIndex))	
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList
		elif len(playerAtHereIndex.positions) < len(playerToMove.positions):
			print("PlayerToMove has more positions than starter at {}. Continue to next button.".format(hereIndex))
			continue
		elif playerAtHereIndex.percentOwned < playerToMove.percentOwned:
			print("PlayerToMove has greater own percentage than starter with game at {}. Moving here.".format(hereIndex))
			button.click()
			playerList = swapPositions(indexToMove, hereIndex, playerList)
			return indexToMove, playerList
		else:
			print("Can't move to {}. Continue to next button.".format(hereIndex))
			continue
	print("No place to move. Go to next player on bench.")
	rowToMove = leftTable.find_element_by_css_selector("[data-idx^='{}']".format(str(indexToMove)))
	time.sleep(1)
	rowToMove.find_element_by_link_text("MOVE").click()
	return indexToMove+1, playerList

"""
Helper function to swap places of two guys in playerList.
Needs to also swap their currentPositions attributes, which makes it slightly trickier.
"""
def swapPositions(indexToMove, hereIndex, playerList):
	startingPosition = playerList[hereIndex].currentPosition
	playerList[hereIndex].setCurrentPosition(playerList[indexToMove].currentPosition)
	playerList[indexToMove].setCurrentPosition(startingPosition)
	playerList[hereIndex], playerList[indexToMove] = playerList[indexToMove], playerList[hereIndex]
	return playerList

"""
Print the playerList better for clearer logging.
"""
def prettyPrint(playerList):
	print("-----------------")
	for i in range(0, len(playerList)):
		player = playerList[i]
		print(player.currentPosition + "(" + str(i) + "): " + player.playerName)

"""
Handler needed for aws lambda.
"""
def lambda_handler(event, context):
	email = os.environ['email']
	password = os.environ['password']
	leagueId = os.environ['leagueId']
	teams = os.environ['teams'].split(",")
	return main(email, password, leagueId, teams)

"""
For if we run in command line
"""
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
	main(args.email, args.password, args.leagueId, "Scranton Stranglers")
	print("--- %s seconds to execute ---" % (time.time() - startTime))
