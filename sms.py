# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from datetime import datetime, timedelta
import dateutil.parser
import logging
from lxml import objectify
import sys
import time
import urllib2

from themylog.client import Client, setup_logging_handler
from themylog.collector.timeline import Timeline
from themylog.level import levels
from themylog.record import Record

setup_logging_handler("sms_daemon")
sys.argv = ["", "sms"]

client = Client()
sms = set()
first_seen_at = {}
while True:
    try:
        xml = urllib2.urlopen("http://192.168.1.1/api/sms/sms-list",
                              '<?xml version="1.0" encoding="UTF-8"?>' +
                              '<request>' +
                              '<PageIndex>1</PageIndex>' +
                              '<ReadCount>20</ReadCount>' +
                              '<BoxType>1</BoxType>' +
                              '<SortType>0</SortType>' +
                              '<Ascending>0</Ascending>' +
                              '<UnreadPreferred>0</UnreadPreferred>' +
                              '</request>').read()
        for Message in objectify.fromstring(xml).Messages.iter("Message"):
            index = int(Message.Index)

            if index in sms:
                continue

            if index not in first_seen_at:
                first_seen_at[index] = datetime.now()
                break
            elif datetime.now() - max(first_seen_at.values()) < timedelta(seconds=10):
                break

            phone = unicode(Message.Phone)
            timeline = Timeline(phone)
            if timeline.contains(index):
                sms.add(index)
                continue

            client.log(Record(datetime=dateutil.parser.parse(unicode(Message.Date)),
                              application="sms",
                              logger=phone,
                              level=levels["report"],
                              msg="%s" % index,
                              args={k.tag: unicode(k) for k in Message.iter()},
                              explanation=unicode(Message.Content)))
            sms.add(index)
            first_seen_at = {}
    except:
        logging.exception("An exception occured")

    time.sleep(1)
