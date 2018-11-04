#!/usr/bin/python3
# Chris Vrabel
# 11/02/18

# Lambda Script for benching today's games if going over max limit games per week.
# Login as League Manager and bench players for each team.

import time
import sys
import os
import setLineup as setter
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
3a) Sits games in starting lineup so team does not exceed max games.
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


	url = "http://fantasy.espn.com/basketball/league/scoreboard?leagueId={}".format(leagueId)
	driver.get(url)
	print("Connected to url")
	WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))
	time.sleep(1)
	# Login Page
	setter.login(email, password, driver)
	gamesRemainingDict = findGamesRemainingForTeams(driver, url, teams)

	print(gamesRemainingDict)

	url = "http://fantasy.espn.com/basketball/tools/lmrostermoves?leagueId={}".format(leagueId)
	for teamName in teams:
		driver.get(url)
		print("Benching games over limit for " + teamName)
		setter.navigateToEditRosterPage(teamName, driver)
		teamGamesRemaining = 20
		try:
			teamGamesRemaining = gamesRemainingDict[teamName]
		except:
			print("Games Remaining Dictionary is empty.")
		benchPlayers(driver, teamGamesRemaining)
		print("Finished benching games for " + teamName)

	driver.quit()
	print("Webdriver quit")
	return "Lambda finished."

"""
Function to find the number of games remaining for each team by navigating to each box score.

returns: Dict of team name, num games remaining (key, value)
"""
def findGamesRemainingForTeams(driver, url, teams):
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
		if all(team in teamGamesRemaining for team in teams):
			print("Found games remaining for all teams in team list.")
			break

	return teamGamesRemaining

"""
Find games remaining for the 2 teams in this box score.

returns: Dict of length 2. team name, num games remaining (key, value)
"""
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

"""
Method which handles the general logic of setting lineup for a team.
1)	Extracts player info from each row on the roster
2) If we are over the games remaining, moves players out of starting lineup.
"""
def benchPlayers(driver, gamesRemaining):
	daysList = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	# tomorrow = daysList[datetime.today().weekday() + 1]
	thisWeek = driver.find_element_by_css_selector("div.Week.currentWeek")
	# tomorrowButton = thisWeek.find_element_by_xpath("//*[contains(text(), '{}')]".format(tomorrow))
	tomorrowButton = thisWeek.find_elements_by_css_selector("div.jsx-1917748593.custom--day")[-1]
	tomorrowButton.click()
	
	leftTable = driver.find_element_by_class_name('Table2__Table--fixed--left')
	rightTable = driver.find_element_by_class_name('Table2__table-scroller')

	playerInfoRows = leftTable.find_elements_by_class_name('Table2__tr--lg')
	playerStatsRows = rightTable.find_elements_by_class_name('Table2__tr--lg')

	playerList = []
	for i in range(0, len(playerInfoRows)):
		player = setter.extractPlayerFromRow(playerInfoRows[i], playerStatsRows[i])
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

	nextIndexToMove = indexOfBlank + 1
	setter.prettyPrint(playerList, str(nextIndexToMove))
	attempts = 0
	if gamesRemaining < 0:
		print("Over the limit.  Moving players out of starting lineup.")
		while attempts < 3:
			try:
				movePlayersOutOfStartingLineup(leftTable, playerList, indexOfBlank, abs(gamesRemaining))
				break
			except Exception as e:
				attempts += 1
				print(e)
	else:
		print("Not over limit.  Doing nothing.")
			
"""
Invoked only if we are over the games player limit.  
Moves numToMove players out of the starting lineup.
Moves the players with lowest percentage owned values to the bench.
"""
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
				if value > currentPercentOwned:
					del indicesToRemove[key]
					indicesToRemove.update({i: currentPercentOwned})
					break

	print("Dict of indices to remove: " + str(indicesToRemove))

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
