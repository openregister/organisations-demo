#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests

from flask.ext.script import Shell, Server, Manager
from pymongo import MongoClient

from organisations_demo import app

app.debug = True
port = os.environ.get('PORT', 8000)

manager = Manager(app)
manager.add_command('server', Server(host="0.0.0.0", port=port))


@manager.command
def populate_index():
    premises_register = app.config['PREMISES_REGISTER']
    feed_url = '%s/feed.json' % premises_register
    page = 1
    db = MongoClient(app.config['MONGO_URI']).get_default_database()
    premises = db.premises
    while True:
        params = {'pageIndex': page, 'pageSize': 1000}
        res = requests.get(feed_url, params)
        if res.json():
            for p in res.json():
                if p['entry']['company']:
                    premises.insert(p)
            page += 1
        else:
            break

if __name__ == '__main__':
    manager.run()
