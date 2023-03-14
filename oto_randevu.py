from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import time
import pytesseract
import base64
from PIL import Image
import io
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.blocking import BlockingScheduler

SEMT = "Semt_Adi" # Bahçelievler
EN_YAKIN_GUN = 5 # 1-15
INTERVAL_TIMER_MINS = 30 # minutes
sender_address = "EMAIL_OUTLOOK" # Change smtp host if you want to use gmail "smtp.gmail.com" instead of 'smtp-mail.outlook.com'
sender_pass = 'PASSWORD'
receiver_address_mime = "EMAIL1, EMAIL2"
receiver_addresses = ["EMAIL1","EMAIL2"]

def anafonk():
	def click(xpath):
		elem = driver.find_element(By.XPATH, xpath)
		elem.click()
		time.sleep(0.5)
		
	def write(xpath,text):
		elem = driver.find_element(By.XPATH, xpath)
		elem.clear()
		elem.send_keys(text)

	def captcha_resolver(xpath):
		time.sleep(0.5)
		elem = driver.find_element(By.XPATH, xpath)
		image_src = elem.get_attribute('src')
		image_src = image_src[22:]
		image = base64.urlsafe_b64decode(str(image_src))       
		img = Image.open(io.BytesIO(image))
		text = pytesseract.image_to_string(img)
		text_digit = ''.join(x for x in text if x.isdigit())
		if(text_digit == ''):
			click(f'//*[@id="divKisi"]/div[1]/div[6]/div/label/a/i')
			captcha_resolver(xpath)
		return text_digit
		
	def is_element_exist(xpath):
		try:
			#identify element
			elem = driver.find_element(By.XPATH, xpath)
			s = elem.text
			print("Element exist -" + s)
			return True
		#NoSuchElementException thrown if not present
		except NoSuchElementException:
			print("Element does not exist")
			return False

	def confirm_error():
		xpath_error = f'/html/body/div[2]/div[2]/div/div/div/div/div/div/div/div[2]/span[2]'
		xpath_confirm = f'/html/body/div[2]/div[2]/div/div/div/div/div/div/div/div[4]/button'
		if(is_element_exist(xpath_error)):
			click(xpath_confirm)
			return True
		return False

	def is_captcha_empty():
		wrong_captcha = f'//*[@id="parsley-id-19"]/li'
		if(is_element_exist(wrong_captcha)):
			return True
		return False

	options = webdriver.ChromeOptions() 
	options.headless = True 
 
	driver = webdriver.Chrome(options=options)
	driver.implicitly_wait(1)
	driver.get("https://randevu.nvi.gov.tr/")
	driver.maximize_window()

	belediyeler = list()


	time.sleep(0.5)
	assert "Randevu Al" in driver.title
	click("/html/body/div/div[1]/div/div/div[2]/form/div/a[3]/div/div/div/p")
	click("/html/body/div[2]/div[2]/div/div/div/div/div/div/div/div[4]/button[1]")
	click(f'//*[@id="pasaport"]/div/div/div/div[1]/div/button')
	write(f'//*[@id="divKisi"]/div[1]/div[1]/div/input', "Halil")
	write(f'//*[@id="divKisi"]/div[1]/div[2]/div/input', "Şen")
	write(f'//*[@id="IdentityNo"]', "25171907620")
	write(f'//*[@id="divKisi"]/div[1]/div[4]/div/div/div[1]/input', "01")
	write(f'//*[@id="divKisi"]/div[1]/div[4]/div/div/div[2]/input', "06")
	write(f'//*[@id="divKisi"]/div[1]/div[4]/div/div/div[3]/input', "1996")
	write(f'//*[@id="divKisi"]/div[1]/div[5]/div/input', "5546876681")

	captcha = captcha_resolver(f'//*[@id="divKisi"]/div[1]/div[6]/div/div/img')
	while(captcha == ''):
		click(f'//*[@id="divKisi"]/div[1]/div[6]/div/label/a/i')
		captcha = captcha_resolver(f'//*[@id="divKisi"]/div[1]/div[6]/div/div/img')
	write(f'//*[@id="divKisi"]/div[1]/div[6]/div/input', captcha)

	click(f'//*[@id="divKisi"]/div[2]/div/button')
	while(confirm_error()):
		captcha = captcha_resolver(f'//*[@id="divKisi"]/div[1]/div[6]/div/div/img')
		while(captcha == ''):
			click(f'//*[@id="divKisi"]/div[1]/div[6]/div/label/a/i')
			captcha = captcha_resolver(f'//*[@id="divKisi"]/div[1]/div[6]/div/div/img')
		write(f'//*[@id="divKisi"]/div[1]/div[6]/div/input', captcha)
		click(f'//*[@id="divKisi"]/div[2]/div/button')
	click(f'/html/body/div/form/section/div/div[2]/div[3]/div/div/a[2]/span')
	time.sleep(5)
	items = driver.find_elements(By.XPATH, f'//*[@id="districtRow"]/div/div/a[*]')
	for item in items:
		texts = item.text
		mekan = texts.split("\n")[0]
		doluluk = texts.split("\n")[1]
		rate = doluluk.split(" ")[2]
		rate = int(rate[1:])
		if(rate == 100):
			continue
		date = texts.split("\n")[2]
		day = int(date.split(".")[0])
		month = int(date.split(".")[1])
		year = int(date.split(".")[2])
		date = datetime(year, month, day)
		now = datetime.now()
		delta = date - now
		belediye = {
			"belediye" : mekan.split(" ")[0],
			"doluluk" : rate,
			"tarih" : date.strftime("%d/%m/%Y"),
			"fark" : delta.days + 1
		}
		belediyeler.append(belediye)
		
	for belediye in belediyeler:
		print(belediye)
  
	driver.quit()

	#Mail section
	mail_content = '''Hello,
	This is a simple mail. There is only text, no attachments are there The mail is sent using Python SMTP library.
	Thank You


	'''
	permission_to_send_mail = False
	for belediye in belediyeler:
		if(belediye["belediye"] == SEMT):
			if(belediye["fark"] < EN_YAKIN_GUN):
				permission_to_send_mail = True
				mail_content = mail_content + belediye["belediye"] + " belediyesinde " + str(belediye["fark"]) + " gün sonra boş yer var."


	if(permission_to_send_mail):
		#Setup the MIME
		message = MIMEMultipart()
		message['From'] = sender_address
		message['To'] = receiver_address_mime
		message['Subject'] = 'A info mail sent by Python. It has an empty session on Bahcelievler Nufus mudurlugu.'   #The subject line
		message.attach(MIMEText(mail_content, 'plain'))
		# set up the SMTP server
		session  = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
		session .starttls()
		session .login(sender_address, sender_pass)
		text = message.as_string()
		session.sendmail(sender_address, receiver_addresses, text)
		session.quit()
		print('Mail Sent')

scheduler = BlockingScheduler()
scheduler.add_job(anafonk, 'interval', minutes=INTERVAL_TIMER_MINS)
scheduler.start()