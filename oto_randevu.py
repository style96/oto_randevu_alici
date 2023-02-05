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

def click(xpath):
	elem = driver.find_element(By.XPATH, xpath)
	elem.click()
	time.sleep(0.5)
	
def write(xpath,text):
	elem = driver.find_element(By.XPATH, xpath)
	elem.clear()
	elem.send_keys(text)

def captcha_resolver(xpath):
	elem = driver.find_element(By.XPATH, xpath)
	image_src = elem.get_attribute('src')
	image_src = image_src[22:]
	image = base64.urlsafe_b64decode(str(image_src))       
	img = Image.open(io.BytesIO(image))
	text = pytesseract.image_to_string(img)
	text_digit = ''.join(x for x in text if x.isdigit())
	if(text_digit == ''):
		text_digit = '0000'
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

driver = webdriver.Chrome()
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
write(f'//*[@id="divKisi"]/div[1]/div[6]/div/input', captcha)
click(f'//*[@id="divKisi"]/div[2]/div/button')
while(confirm_error()):
	captcha = captcha_resolver(f'//*[@id="divKisi"]/div[1]/div[6]/div/div/img')
	write(f'//*[@id="divKisi"]/div[1]/div[6]/div/input', captcha)
	click(f'//*[@id="divKisi"]/div[2]/div/button')
click(f'/html/body/div/form/section/div/div[2]/div[3]/div/div/a[2]/span')
items = driver.find_elements(By.XPATH, f'//*[@id="districtRow"]/div/div/a[*]')
for item in items:
	texts = item.text
	mekan = texts.split("\n")[0]
	doluluk = texts.split("\n")[1]
	rate = doluluk.split(" ")[2]
	rate = int(rate[1:])
	if(rate == 100):
		break
	date = texts.split("\n")[2]
	day = int(date.split(".")[0])
	month = int(date.split(".")[1])
	year = int(date.split(".")[2])
	date = datetime(year, month, day)
	now = datetime.now()
	delta = date - now
	belediye = {
		"belediye" : mekan,
		"doluluk" : rate,
		"tarih" : date,
		"fark" : delta.days + 1
	}
	belediyeler.append(belediye)
	
for belediye in belediyeler:
	print(belediye)

#### DEPRECATED CODES WORKS BUT NOT REQUIRED FOR NOW ####
"""
img_cv2 = cv2.imread("captcha.png")
text = pytesseract.image_to_string(img_cv2)
print("img_cv2.png")
print(''.join(x for x in text if x.isdigit()))

gry = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
cv2.imwrite('gry.png',gry) # save image
text = pytesseract.image_to_string(gry)
print("gry.png")
print(''.join(x for x in text if x.isdigit()))

(h, w) = gry.shape[:2]
gry = cv2.resize(gry, (w*2, h*2))
cv2.imwrite('gry_resize.png',gry) # save image
text = pytesseract.image_to_string(gry)
print("gry_resize.png")
print(''.join(x for x in text if x.isdigit()))

cls = cv2.morphologyEx(gry, cv2.MORPH_CLOSE, None)
cv2.imwrite('gry_close.png',cls) # save image
text = pytesseract.image_to_string(cls)
print("gry_close.png")
print(''.join(x for x in text if x.isdigit()))

thr = cv2.threshold(cls, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
cv2.imwrite('gry_Threshold.png',thr) # save image
text = pytesseract.image_to_string(thr)
print("gry_Threshold.png")
print(''.join(x for x in text if x.isdigit()))
"""
"""
gray = img.convert('L')
gray.save('captcha_gray.png')
bw = gray.point(lambda x: 0 if x < 1 else 255, '1')
bw.save('captcha_thresholded.png')
text = pytesseract.image_to_string(img)
print(''.join(x for x in text if x.isdigit()))
"""


print(elem.is_displayed())

