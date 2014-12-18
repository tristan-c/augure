#!/usr/bin/env python
# coding: utf-8
import time, os , json, logging
import schedule, requests
from envelopes import Envelope, GMailSMTP
from .daemon3 import daemon as Daemon

class Worker(Daemon):
    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.config = None

    def run(self):
        if not self.config:
            self.config = self.loadConfiguration()

        self.initLogger(self.config.get("logPath",None))

        self.logger.info("Augure is watching")
        schedule.every().minute.do(self.check)

        while True:
            self.logger.debug("check pending job")
            schedule.run_pending()
            time.sleep(1)

    def check(self):
        for url in self.config['urls']:
            r = requests.get(url)
            if r.status_code != 200:
                message = "%s: status %s" % (url,r.status_code)
                self.logger.warning(message)

                if self.config['emailRecipient']:
                    self.sendMail(message)

    def sendMail(self,text):
        self.logger.debug("Building mail")

        envelope = Envelope(
            from_addr=('augure@augure.nowhere'),
            to_addr=(self.config['emailRecipient']),
            subject='Augure has spoken',
            text_body=text
        )

        try:
            self.logger.debug("Sending mail")
            envelope.send('smtp.googlemail.com', login=self.config["emailLogin"],
                  password=self.config["emailPassword"], tls=True)
            self.logger.debug("Mail sent")
        except Exception as e:
            self.logger.error(e)

    def loadConfiguration(self, filename=None):
        configFile = None
        if filename and os.path.isfile(filename):
            configFile = filename
        if os.path.isfile("/etc/augure/augure.conf"):
            configFile = "/etc/augure/augure.conf"

        homeConfiguration = "%s%s" % (os.path.expanduser("~"),"/.augure/augure.conf")
        if os.path.isfile(homeConfiguration):
            configFile = homeConfiguration
        
        if not configFile:
            raise Exception("No Configuration file found")

        try:
            with open(configFile) as data_file:
                data = json.load(data_file)
                self.config = data
                return data
        except Exception as e:
            logging.error(e)
            raise Exception("Error in %s: %s" % (configFile,e))


    def initLogger(self,path="%s%s" % (os.path.expanduser("~"),"/augure.log")):
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:%(message)s',
            filename=path,
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)

