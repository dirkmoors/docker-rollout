# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import requests

DEPLOYMENT_NOTIFICATION_URL = 'https://api.newrelic.com/v2/applications/{application_id}/deployments.json'


def notify_deployment(api_key, app_id, app_revision, user=None, output_handler=None):
    # Set default output handler
    output_handler = output_handler or sys.stdout.write

    deployment_url = DEPLOYMENT_NOTIFICATION_URL.format(application_id=app_id)

    deployment = {
        'revision': app_revision,
    }
    if user:
        deployment['user'] = user

    r = requests.post(deployment_url, json={'deployment': deployment}, headers={'X-Api-Key': api_key})
    output_handler(r.json())