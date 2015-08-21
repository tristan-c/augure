Augure - Supervision at its dumbest
======

Augure is a tiny daemon script to look if your websites are down (not answering with http code 200) then send you a email.

##Installation:

Following instruction use a virtualenv, it's not a requirement.

```bash
git clone https://github.com/tristan-c/augure.git
cd augure
pyvenv venv
source venv/bin/activate
python setup.py install

```

Then you can use it like a daemon:

```bash
augure start
augure restart
augure stop
augure status
```

##Config file :
Augure will first search for 
* /etc/augure.conf
* /etc/augure/augure.conf
* ~/.augure/augure.conf

If there is no config file Augure will not be happy =(

```json
{
    "urls": ["http://first_url.com/",
        "http://second_url.com/",
        "http://thirs_url.com/"],
    "emailRecipient": "tristan@carranante.name",
    "emailServer": "smtp.googlemail.com",
    "emailLogin": "my_gmail_account@gmail.com",
    "emailPassword": "my_gmail_password",
    "logPath": "/var/log/augure.log"
}
```
**Required:**  
* **urls**: URLs to look for.  
* **emailRecipient**: Mail Address Recipient for alerts.  

**Optional:**  
* **emailServer**: Address of external SMTP server if your server doesn't have one.  
* **emailLogin"**: Login for external SMTP.  
* **emailPassword"**: Password for external SMTP.  
* **logPath"**: Path for logfile , default to /tmp/augure.log.

##License:

The MIT License (MIT)  
