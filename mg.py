# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from celery import Celery
from flask import *
import hashlib
import hmac

from themylog.config import find_config, read_config

app = Flask(__name__)

config = read_config(find_config())

celery = Celery()
celery.config_from_object(config["celery"])


def verify_request():
    if request.form["signature"] != hmac.new(b"<API key>",
                                             request.form["timestamp"] + request.form["token"],
                                             hashlib.sha256).hexdigest():
        abort(401)


@app.route("/vtb24", methods=["POST"])
def vtb24():
    verify_request()
    celery.send_task("collectors.vtb24")
    return Response("")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
