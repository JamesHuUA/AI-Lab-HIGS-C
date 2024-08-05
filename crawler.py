'''
Last Updated on Aug 5, 2024

@author: James Lee Hu, UArizona MIS PhD Student
'''
import os, re
from time import sleep
import random
import pandas as pd
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup


def sleep4Captcha():
	'''
    Function that randomly pauses crawling to avoid Google's Captcha System. Randomness emulates human behavior. 
    	Values can be modified to speed up or slow down crawling. 
    	Trade-off is that faster crawling activates more Captchas and vice-versa.

    Parameters
    ----------
	None

    Returns
    -------
    None
	'''
	sleep(5 + random.randint(-2,4))


def crawlHomepage(browser, savePages, name):
	'''
	Crawl function for the Google Scholar homepage

    Parameters
    ----------
	None
	browser : selenium.Webdriver
        Selenium Webdriver object that operates the online crawling. Is responsible for the pop-up Firefox window 
    savePages : bool
        Enable saving of webpages
    name : str
        Name of the current scholar being crawled

    Returns
    -------
    output : dict
        Dictionary of every scholar result and the url to their Google Scholar profile page
	'''

	#Initialize crawl with Google Scholar homepage
	url = "https://scholar.google.com"
	browser.get(url)
	sleep4Captcha()

	#Navigate to search bar, enter name into search bar, submit for search result
	searchBar = browser.find_element(By.XPATH, "//input[@class='gs_in_txt gs_in_ac']")
	searchBar.clear()
	searchBar.send_keys(name)
	searchBar.submit()
	sleep4Captcha()

	#Navigate to and extract all profile links present on Google Scholar search result page
	htmlContent = browser.page_source
	soup = BeautifulSoup(htmlContent, 'html.parser')
	profileList = soup.find("div",attrs={"class":"gs_r"})
	profileList = profileList.table.find("td",attrs={"valign":"top"})
	profileList = profileList.findAll('h4',attrs={"class":"gs_rt2"})

	#Reformat extracted names and links into readable names and workable links
	output = {}
	for profile in profileList:
		profile = profile.a
		profileURL = 'https://scholar.google.com/' + profile.get('href')
		profileName = profile.get_text().replace("</b>", '')
		
		output[profileName] = profileURL

	#Saves webpage if allowed
	if savePages:
		f = open(homeSaveDir + name + '.html', 'w', encoding='utf-8')
		f.write(htmlContent)
		f.close()

	return output


def crawlProfile(browser, savePages, name, url):
	'''
	Crawl function for the individual Google Scholar profile pages

    Parameters
    ----------
	browser : selenium.Webdriver
        Selenium Webdriver object that operates the online crawling. Is responsible for the pop-up Firefox window
    savePages : bool
        Enable saving of webpages
    name : str
        Name of the current scholar being crawled 
    url : str
        URL to the Google Scholar profile page of the current scholar 

    Returns
    -------
    hIndex : str
        H-Index found on the profile page
	'''

	#Initialize crawl with Google Scholar profile page
	browser.get(url)
	sleep4Captcha()

	#Navigate to and extract H-Index
	htmlContent = browser.page_source
	soup = BeautifulSoup(htmlContent, 'html.parser')
	navi = soup.find("table",attrs={"id":"gsc_rsb_st"}).tbody
	navi = navi.findAll("tr")[1]
	hIndex = navi.findAll('td')[1].get_text()
	
	#Saves webpage if allowed
	if savePages:
		f = open(profileSaveDir + name + '.html', 'w', encoding='utf-8')
		f.write(htmlContent)
		f.close()

	return hIndex

#Main Function
def main()
	#Save paths for homepages and profile pages
	homeSaveDir = './pages/'										#Directory containing saved homepages
	profileSaveDir = './profiles/'									#Directory containing saved profile pages
	savePages = True 												#Set to true to enable webpage saving using the above directories. Set to False to speed up process and save drive space
	
	#Paths to important CSVs
	initialScholars = './names.csv' 								#Initial list of names
	hindexSavePath = './results/hIndexes.csv'  						#Crawler results of saved H-indexes
	skippedSavePath = './results/skipped.csv'  						#Crawler results of skipped scholars
	saveInterval = 5												#How many scholars are crawled before saving current crawler results

	#Initialize selenium browser
	service = Service(executable_path = './geckodriver') 			#Ensure this is the correct path to the downloaded geckodriver
	opts = FirefoxOptions()
	browser = webdriver.Firefox(service = service, options = opts)

	#Load list of scholars
	namesDf = pd.read_csv(initialScholars)

	#Initlialize lists for recording results
	crawledNames = []
	crawledHIndexes = []
	skipped = []
	redo = []
	skipLimit = 5 													#How many skips are tolerated before process is paused for possible Captcha

	#Initialize progress bar and counter for consecutive skips
	progressBar = tqdm(range(namesDf.shape[0]), total=namesDf.shape[0])
	consecutiveSkips = 0
	for index, row in namesDf.iterrows():
		currentScholarName = row['Name']
		progressBar.set_description("Processing: {name}".format(name = currentScholarName))

		#Attempt to get Google Scholar profile page
		try:
			#If succesful, consecutiveSkips reset to 0
			profiles = crawlHomepage(browser, savePages, currentScholarName)
			consecutiveSkips = 0
		except:
			#If failed, profiles set to empty dictionary, skipping next for loop.
			skipped.append(currentScholarName)
			profiles = {}
			consecutiveSkips += 1

		#Iterate through each profile pages and extract H-index
		for profileName in profiles:
			currentHIndex = crawlProfile(browser, savePages, profileName, profiles[profileName])
			crawledNames.append(profileName)
			crawledHIndexes.append(currentHIndex)

		#At the saveInterval, write results to the CSVs. Past CSVs will be overriten
		if index % saveInterval == 0:
			pd.DataFrame().from_dict({'Name': crawledNames, 'H-Index': crawledHIndexes}).to_csv(hindexSavePath, index = False)
			pd.DataFrame().from_dict({'Name': skipped}).to_csv(skippedSavePath, index = False)

		#Update progress bar
		progressBar.update(1)

		#If a certain amount of consecutive skips are detected, pause crawling indefinitely
		if consecutiveSkips >= skipLimit:
			consecutiveSkips = 0

			#Prints message and waits for user input in order to resume crawling
			print("{skipLimit} consecutive skips detected.".format(skipLimit = skipLimit))
			print("If Captcha is active, please complete it and enter anything except 'no' into the CMD.")
			if input("If Captcha is not active, enter 'no' without quotes into the CMD.").lower() == 'no':
				#If Captcha was not active, resumes crawling without extra actions
				pass
			else:
				#If Captcha was active, records past skipped scholars for reprocessing
				redo.extend(skipped[-skipLimit:])

	#Converge first progress bar
	progressBar.set_description('Initial Crawl Finished')
	progressBar.close()

	#Remove duplicates in redo list
	redo = list(set(redo)) 

	#Repeat of previous loop for scholars in the redo list
	progressBar = tqdm(range(len(redo)), total=len(redo))
	consecutiveSkips = 0
	for i in range(len(redo)):
		currentScholarName = redo[i]
		progressBar.set_description("Reprocessing: {name}".format(name = currentScholarName))

		try:
			#Each succesful redo crawl will remove scholar from the skipped list
			profiles = crawlHomepage(browser, savePages, currentScholarName)
			consecutiveSkips = 0
			skipped.remove(currentScholarName)
		except:
			profiles = {}
			consecutiveSkips += 1

		for profileName in profiles:
			currentHIndex = crawlProfile(browser, savePages, profileName, profiles[profileName])
			crawledNames.append(profileName)
			crawledHIndexes.append(currentHIndex)

		if i % saveInterval == 0:
			pd.DataFrame().from_dict({'Name': crawledNames, 'H-Index': crawledHIndexes}).to_csv(hindexSavePath, index = False)
			pd.DataFrame().from_dict({'Name': skipped}).to_csv(skippedSavePath, index = False)

		progressBar.update(1)

		if consecutiveSkips >= skipLimit:
			consecutiveSkips = 0
			print("{skipLimit} consecutive skips detected.".format(skipLimit = skipLimit))
			print("If Captcha is active, please complete it and enter anything except 'no' into the CMD.")
			if input("If Captcha is not active, enter 'no' without quotes into the CMD.").lower() == 'no':
				pass
			else:
				#Instead of extending redo list, i is iterated backwards to re-crawl skipped scholars
				i -= skipLimit

	#At end of entire process, save one last time for all results
	pd.DataFrame().from_dict({'Name': crawledNames, 'H-Index': crawledHIndexes}).to_csv(hindexSavePath, index = False)
	pd.DataFrame().from_dict({'Name': skipped}).to_csv(skippedSavePath, index = False)
	
	#Displays stats in final progress bar description
	progressBar.set_description(
		"{initialSize} Scholars Crawled, {resultSize} H-Indexes Saved, {skippedSize} Scholars Skipped".format(
			initialSize = namesDf.shape[0],
			resultSize = len(crawledHIndexes), 
			skippedSize = len(skipped)))
	progressBar.close()

if __name__ == "__main__":
	main()