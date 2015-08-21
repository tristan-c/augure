#!/usr/bin/env python
# coding: utf-8
import time
import os
import json
import logging

import schedule
import requests
from envelopes import Envelope, SMTP

from .daemon3 import Daemon


class Worker(Daemon):

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)

        self.config = self.load_configuration()

        #check if external mail server
        self.external_mail_server = False
        if self.config.get("emailServer",None):
            if self.config.get("emailLogin",None) and \
               self.config.get("emailPassword",None):
               self.external_mail_server = True

        self.init_logger(self.config.get("logPath", None))

        self.urlStates = {}

    def run(self):
        self.logger.info("Augure is watching")
        schedule.every().minute.do(self.check)
        self.check()

        while True:
            self.logger.debug("check pending job")
            schedule.run_pending()
            time.sleep(1)

    def check(self):
        for url in self.config['urls']:
            r = None
            try:
                r = requests.get(url)
            except:
                pass

            if not r or r.status_code != 200:
                message = "%s is not accessible" % (url)
                if r and r.status_code:
                    message = "%s, status %s" % (message, r.status_code)
                self.logger.warning(message)

                if self.config.get('emailRecipient', None):

                    # if state was ok before (anti spam)
                    if self.urlStates.get(url, True):
                        self.urlStates[url] = False
                        self.send_mail(message)

            else:
                self.urlStates[url] = True

    def send_mail(self, text):
        self.logger.debug("Building mail")

        envelope = Envelope(
            from_addr=('augure@augure.nowhere'),
            to_addr=self.config.get('emailRecipient', None),
            subject='The Augure has spoken',
            text_body=text
        )

        try:
            self.logger.debug("Sending mail")
       
            if self.external_mail_server:
                envelope.send(
                    self.config.get("emailServer"), 
                    login=self.config["emailLogin"],
                    password=self.config["emailPassword"], tls=True
                )
            else:
                #if no mail in config we use local mail server
                envelope.send('localhost', port=25)

            self.logger.debug("Mail sent")
        except Exception as e:
            self.logger.error(e)

    def load_configuration(self, filename=None):
        configFile = None
        if filename and os.path.isfile(filename):
            configFile = filename
        if os.path.isfile("/etc/augure/augure.conf"):
            configFile = "/etc/augure/augure.conf"
        if os.path.isfile("/etc/augure/augure.conf"):
            configFile = "/etc/augure.conf")

        home_conf = "%s%s" % (os.path.expanduser("~"),"/.augure/augure.conf")
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
            raise Exception("Error in %s: %s" % (configFile, e))

    def init_logger(self, path="/tmp/augure.log"):
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:%(message)s',
            filename=path,
            level=logging.INFO
            
        self.logger = logging.getLogger(__name__)
