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

QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/244220539866/Q1'

ES_USER = 'prateek'
ES_PASS = 'Prateek@1709'
ES_QUERY = "https://search-restaurants-tjdy4o57veqr6t73mf4rgl4o44.us-east-1.es.amazonaws.com/restaurants/_search?q={cuisine}&size={size_limit}"

DYNAMO_DB_TABLE_NAME = 'yelp-restaurants'