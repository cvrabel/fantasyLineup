#!/usr/bin/python3
# Chris Vrabel
# 10/19/18

# Lambda Script for Fantasy Basketball lineup setting.
# Login for specified team and set lineup.

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
3)  Sets lineup for each team in list
"""
def main(email, password, leagueId, teamId):
	
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

	url = "http://fantasy.espn.com/basketball/team?/team?leagueId={}&teamId={}".format(leagueId, teamId)
	driver.get(url)
	print("Connected to ESPN fantasy basketball.")
	WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))
	time.sleep(1)
	
	# Login Page
	setter.login(email, password, driver)
	time.sleep(4)
	print("Setting lineup for teamId: ".format(teamId))
	setter.setLineup(driver)
	print("Finished setting lineup.")
	
	driver.quit()
	print("Webdriver quit")
	return "Lambda finished."

"""
Handler needed for aws lambda.
"""
def lambda_handler(event, context):
	email = os.environ['email']
	password = os.environ['password']
	leagueId = os.environ['leagueId']
	teamId = os.environ['teamId']
	return main(email, password, leagueId, teamId)

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
	main(args.email, args.password, args.leagueId)
	print("--- %s seconds to execute ---" % (time.time() - startTime))
