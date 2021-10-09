import json
import boto3
import logging
import math
import dateutil.parser
import datetime
import time
import random
import urllib3
import os

QUEUE_URL = ''

ES_USER = ''
ES_PASS = ''
ES_QUERY = ""

DYNAMO_DB_TABLE_NAME = 'yelp-restaurants'
