#! python3
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request
import codecs
import os
import datetime

url = input("enter url:")
link_file_name = str(datetime.date.today()) + " " + input("enter name for link file:")
urlstart = "www.youtube.com/" #prefix
looking = "watch?v=" #word to search for

def get_source_bs4(url): #no scroll & no javascript
	
	###request headers
	headers = {}
	headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"

	###request
	req = urllib.request.Request(url, headers = headers)
	page = urllib.request.urlopen(req)

	#reading the request
	web_data = BeautifulSoup(page, 'lxml')
	#respData = page.read()    ###instead without BeautifulSoup

	return web_data

def get_source_selenium(url): #with infinite scroll

	#set webbrowser options
	#profile = webdriver.FirefoxProfile('C:/Users/Toshiba/AppData/Roaming/Mozilla/Firefox/Profiles/#YOUR_PROFILE_NAME#')
	profile.set_preference("media.volume_scale", "0.0")
	#profile.set_preference('browser.download.folderList', 2) # custom location
	#profile.set_preference('browser.download.manager.showWhenStarting', False)
	#profile.set_preference('browser.download.dir', 'C:/Users/Toshiba/Desktop/python/linkscrapper')
	#profile.set_preference('browser.helperApps.neverAsk.saveToDisk', "image/png,image/jpeg")

	#open website
	browser = webdriver.Firefox(firefox_profile=profile,executable_path='/geckodriver.exe')
	#browser = webdriver.Chrome(executable_path='/linkscrapper/chromedriver.exe')
	browser.get(url)

	# Selenium script to scroll to the bottom, wait 5 seconds for the next batch of data to load, then continue scrolling.
	# It will continue to do this until the page stops loading new data.
	last_position = browser.execute_script("return window.scrollY")

	a = True;last_position=0
	while a == True:
		time.sleep(5)
		browser.execute_script("window.scrollBy(0,999999999)")
		next_position = browser.execute_script("return window.scrollY")
		if last_position == next_position:
			a = False
		last_position = next_position

	# Now that the page is fully scrolled, grab the source code.
	source_data = browser.page_source

	browser.quit()

	# Throw your source into BeautifulSoup and start parsing!
	web_data = BeautifulSoup(source_data, "lxml")

	#javascript codes:
	#getElementById, getElementsByName, getElementsByClassName, getElementsByTagName
	#window.scrollTo(0, 0), window.scrollBy(dx,dy), scroll(x,y)
	###other option: Key Press "END"

	return web_data

def save_source(web_data):

	###save data in 
	data = codecs.open('website.txt','w', "utf-8", errors='ignore')
	data.write(str(web_data))
	data.close()

	return

def process_source_new(urlstart,looking): #extract links without deleting
	
	datasearch = codecs.open('website.txt','r','utf-8',errors='ignore')
	linkset = set()

	for line in datasearch:
		pos = 0
		try:
			counter = int(line.count(looking))
			c = 0
			for c in range(0,counter):
				pos = line.index(looking, pos)
				linkset.add(urlstart+line[pos:pos+19]+"\n")
				c += 1
		except ValueError:
			break

	datasearch.close()

	return linkset

def process_source_old(urlstart,looking): #extract links and delete processed parts
	
	datasearch = codecs.open('website.txt','r','utf-8',errors='ignore')
	linkset = set()
	
	for line in datasearch:
		try:
			#get position of the next "looking" word
			pos = line.index(looking)
			#remove everything before "looking" word
			line = line.replace(line[0:pos],"")
			#extract "looking" word as an link
			linkset.add(urlstart+line[0:19]+"\n")
			#remove extracted link
			line = line.lstrip(line[0:19])
		except ValueError:
			continue

	datasearch.close()

	return linkset

def save_links(linkset,link_file_name):

	links = open(link_file_name+".txt","a")

	full = True
	while full == True:
		try:
			links.write(linkset.pop())
		except KeyError:
			full = False

	links.close()
	return

web_data = get_source_selenium(url) #or web_data = get_source_bs4(url)
save_source(web_data)
linkset = process_source_new(urlstart,looking) #or linkset = process_source_old(urlstart,looking)

print(str(len(linkset))+' links found')

save_links(linkset,link_file_name)

os.remove('website.txt')
print('done')
time.sleep(5)