# Chris Vrabel
# 2/17/18

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys

def setLineup(username, password):
	print(username)
	print(password)

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('headless')
	driver = webdriver.Chrome(chrome_options=chrome_options)
	# driver.set_window_size(1920, 1080)
	# driver.maximize_window()
	print("here1")
	driver.get('http://games.espn.com/fba/signin?redir=http%3A%2F%2Fgames.espn.com%2Ffba%2Fclubhouse%3FteamId%3D1%26leagueId%3D163326%26seasonId%3D2018')
	driver.find_element_by_link_text('Username or Email Address').send_keys(username)	
	# driver.find_element_by_id('login-passwd').send_keys(password)
	# time.sleep(8)
	# driver.find_element_by_name('signin').click()
	# time.sleep(8)

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
	driver.quit()


if __name__ == '__main__':
	setLineup(sys.argv[1], sys.argv[2])