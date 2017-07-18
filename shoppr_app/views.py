from django.shortcuts import render
from django.http import HttpResponse
import os, datetime, time
import json, threading, re, cgi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.command import Command
from pyvirtualdisplay import Display
import redis, httplib, socket

r = redis.Redis('localhost')
count = total_user = 0
following = media = {}

def get_status(driver):
    try:
        driver.execute(Command.STATUS)
        return "Alive"
    except (socket.error, httplib.CannotSendRequest):
        return "Dead"

def login(driver, username, password):
	driver.get("https://www.instagram.com/accounts/login/")
	driver.find_element_by_name('username').send_keys(username)
	driver.find_element_by_name('password').send_keys(password)
	driver.find_element_by_xpath("//span/button").click()
	# Wait for the homepage to load
	WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Profile")))

def logout(driver):
	# Click Profile
	WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Profile"))).click()
	# Click Options
	WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Options"]'))).click()
	# Click Log out
	WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Log out"]'))).click()

def scrape_following(driver):
	i = count = 0
	following_dict = {}
	if 'logged-in' in driver.page_source:
		# Click Profile
		driver.find_element_by_link_text('Profile').click()
		# Wait for the profile page to load
		WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/kwkm92/following/"]')))
		if '@kwkm92' in driver.page_source:
			# Click Following
			driver.find_element_by_xpath('//a[@href="/kwkm92/following/"]').click()
			# Wait for the following modal to load
			xpath = "//div[@style='position: relative; z-index: 1;']/div/div[2]/div/div[1]"
			WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
			# Scrolling down, to load more users
			print "Getting all users this account follows"
			while 1:
				driver.execute_script("document.querySelector('div[role=dialog] ul').parentNode.scrollTop=1e100")
				try:
					WebDriverWait(driver, 20).until(scroll_following)
				except:
					break;
			# Finally, scrape the followers
			print "Scraping all following users.."
			xpath = "//div[@style='position: relative; z-index: 1;']//ul/li/div/div/div/div/a"
			following_elems = driver.find_elements_by_xpath(xpath)
			for element in following_elems:
				following_dict[i] = element.text
				i += 1
			print "Total following users is: %s" %i
			print "Scraping done.."
			# Quit from following list
			WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//body/div/div/button'))).click()
			return following_dict, i

def scroll_following(driver):
	global count
	new_count = len(driver.find_elements_by_xpath("//div[@role='dialog']//li"))
	if count != new_count:
		count = new_count
		print "%s following" %count
		return True
	else:
		return False

def get_following():
	global following, total_user
	json_dict = {}
	# using Chrome WebDriver
	display = Display(visible=0, size=(800, 600))
	display.start()
	driver = webdriver.Chrome()
	username = "#username"
	password = "#password"
	login(driver, username, password)
	following, total_user = scrape_following(driver)
	logout(driver)
	driver_status = get_status(driver)
	print driver_status	
	driver.quit()
	driver_status = get_status(driver)
	print driver_status
	if (driver_status == "Alive"):
		driver.quit()	
	print driver_status
	display.stop()
        json_dict['total_user'] = total_user
        json_dict['following'] = following
        json_data = json.dumps(json_dict)
        r.set("following_list", json_data)
        r.set("total_user", total_user)

def get_username_data(driver, username):
	now = datetime.datetime.now()
	today = str(now.strftime("%b %d, %Y"))
	# Getting the user's biography
	driver.get("https://www.instagram.com/%s/" %username)
	a = driver.page_source
	regex = 'biography": (.{1,1000}|null), "full_name":'
	match = re.search(regex, a)
	if match:
		bio = match.group(1)
		bio = unicode(bio).decode('unicode-escape')
	# Getting the other information
	driver.get("https://www.instagram.com/%s/media/" %username)       # "/media" shows in json, only 20 file for sandbox user
	b = driver.find_element_by_xpath('//body/pre')
	b = b.text
	data = json.loads(b)
	totalpost = b.count('can_delete_comments')
	post = {}
	j = 0
	for i in range(totalpost):
		created_time = int(data['items'][i]['created_time'])
		created_date = str(time.strftime("%b %d, %Y", time.localtime(created_time)))
		if today == created_date:
			data_dict = {}
			data_dict['created_date'] = created_date
			data_dict['id'] = data['items'][i]['user']['id']
			data_dict['username'] = data['items'][i]['user']['username']
			data_dict['profile_picture'] = data['items'][i]['user']['profile_picture']
			data_dict['bio'] = bio
			try:
				data_dict['caption'] = data['items'][i]['caption']['text']
			except:
				data_dict['caption'] = "null"
			data_dict['image_url'] = data['items'][i]['images']['standard_resolution']['url']
			post[j] = data_dict
			j += 1
	json_data = json.dumps(post)
	return json_data

def update_media():
	global following, media
	display = Display(visible=0, size=(800, 600))
	display.start()
	driver = webdriver.Chrome()
	username = "kwkm92"
	password = "P34^J@eYok#l"
	login(driver, username, password)
	for i in range(len(following)):
		check = False
		while check == False:
			try:
				print "%s. updating media %s" %(i, following[i])
				r.set(following[i], get_username_data(driver, following[i]))
				check = True
			except:
				print "error"
				check = False
	driver.get("https://www.instagram.com/")
	logout(driver)
	driver_status = get_status(driver)
        print driver_status
        driver.quit()
        driver_status = get_status(driver)
        print driver_status
        if (driver_status == "Alive"):
                driver.quit()
	print driver_status
        display.stop()

def get_list(request):
	if request.method == 'GET':
		if int(r.get("total_user")) == None:
			json_error = {"result": False, "error":"retry"}
			json_data = json.dumps(json_error)
			return HttpResponse(json_data, content_type="application/json")
		else:
			json_data = r.get("following_list")
			return HttpResponse(json_data, content_type="application/json")

def get_media(request, username):
	if request.method == 'GET':
		try:
			json_data = r.get(username)
#			bio = cgi.escape(bio).encode('ascii', 'xmlcharrefreplace')
			return HttpResponse(json_data, content_type="application/json")
		except:
			json_error = {"status":"404", "error":"user_not_found"}
			json_data = json.dumps(json_error)
			return HttpResponse(json_data, content_type="application/json")

class thread_handler():
	def follow_thread(self):
		if (float(r.get("follow_time")) + float(10000.0)) < time.time():
			threadLock.acquire()
			print "Update following"
			r.set("follow_time", float(time.time()))
			get_following()
			threadlog = open((os.path.join(os.path.dirname(os.path.dirname(__file__)), "follow_thread_logfile.txt")), 'a')
			now = datetime.datetime.now()
			threadtime = str(now.strftime("%b %d, %Y %H:%M"))
			threadlog.write("%s %s\n" %(r.get("follow_time"), time.time()))
			threadlog.write("Datetime: %s\n" %threadtime)
			threadlog.write("Thread start\n\n")
			threadlog.close()
			threadLock.release()
	def update_media(self):
		if (float(r.get("update_time")) + float(10000.0)) < time.time():
			threadLock.acquire()
			print "Update getmedia"
			r.set("update_time", float(time.time()))
			update_media()
			threadlog = open((os.path.join(os.path.dirname(os.path.dirname(__file__)), "update_thread_logfile.txt")), 'a')
			now = datetime.datetime.now()
			threadlog.write("%s %s\n" %(r.get("update_time"), time.time()))
			threadtime = str(now.strftime("%b %d, %Y %H:%M"))
			threadlog.write("Datetime: %s\n" %threadtime)
			threadlog.write("Thread start\n\n")
			threadlog.close()
			threadLock.release()

class timer_thread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		while 1:
			handler = thread_handler()
			handler.follow_thread()
			handler.update_media()
			time.sleep(21600)

threadLock = threading.Lock()
r.set("follow_time", 0.0)
r.set("update_time", 0.0)
thread = timer_thread()
thread.start()

