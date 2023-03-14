# oto_randevu_alici
Selenium kullanarak randevu.nvi.gov.tr sitesinden otomatik randevu izleyici ve En yakın randevu gününü mail atan bot. 

## Quick Start
Change Variables for yourself.
```Python
SEMT = "Semt_Adi" # Bahçelievler
EN_YAKIN_GUN = 5 # 1-15
INTERVAL_TIMER_MINS = 30 # minutes
sender_address = "EMAIL_OUTLOOK" # Change smtp host if you want to use gmail "smtp.gmail.com" instead of 'smtp-mail.outlook.com'
sender_pass = 'PASSWORD'
receiver_address_mime = "EMAIL1, EMAIL2"
receiver_addresses = ["EMAIL1","EMAIL2"]
```
