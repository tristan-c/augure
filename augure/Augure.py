#!/usr/bin/env python
# coding: utf-8
import time
import os
import json
import logging
import signal
import time

import schedule
import requests
from envelopes import Envelope, SMTP
import requests

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

class Daemon:
    def __init__(self, *args, **kwargs):
        self.load_configuration()
        self.init_logger(self.config.get("logPath", None))

        self.url_states = {}
        self.external_mail_server = False
        madatory_mail_options = ['emailServer','emailLogin','emailPassword',
                                'emailRecipient']

        if all(key_ in  self.config for key_ in madatory_mail_options):
               self.external_mail_server = True
        else:
            self.logger.warning('No or bad mail informations given')



    def run(self):
        killer = GracefulKiller()

        self.logger.info("Augure is watching")
        schedule.every().minute.do(self.check_url)
        self.check_url()

        while True:
            self.logger.debug("check pending job")
            schedule.run_pending()
            time.sleep(5)
            if killer.kill_now:
                break

        self.logger.info("Augure stop watching")

    def check_url(self):
        urls = self.config.get('urls', [])
        self.logger.info("Augure watch %i urls" % len(urls))
        for url in urls:
            try:
                r = requests.get(url)
            except:
                self.logger.warning('request to %s failed' % url)
                return False

            if r.status_code == requests.codes.ok:
                self.url_states[url] = True
                return True

            message = "%s, status %s" % (url, r.status_code)
            self.logger.warning(message)

            if self.url_states.get(url, True):
                self.url_states[url] = False
                self.send_mail(message)

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

    def load_configuration(self):
        conf_file = None
        if os.path.isfile('/etc/augure/augure.conf'):
            conf_file = open('/etc/augure/augure.conf')
        else:
            conf_path = "%s%s" % (os.path.expanduser("~"),"/.augure/augure.conf")
            if os.path.isfile(conf_path):
                conf_file = open(conf_path)

        if not conf_file:
            raise Exception("can't find conf file")

        self.config = json.load(conf_file)

    def init_logger(self, path="/tmp/augure.log"):
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:%(message)s',
            filename=path,
            level=logging.INFO)

        self.logger = logging.getLogger(__name__)
