import boto3
import datetime
import requests
import json, os
from decimal import Decimal
from datetime import datetime
from elasticsearch import Elasticsearch
from botocore.exceptions import ClientError

API_KEY = ''
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

ES_USER = ''
ES_PASS = ''
ES_URL = ''

DYNAMO_DB_TABLE_NAME = 'yelp-restaurants'

AWS_REGION_NAME = 'us-east-1'

cuisine_types = ['carribean' , 'turkish', 'peruvian', 'vietnamese','turkish', 'greek', 'thai', 'chinese', 'italian', 'mexican', 'japanese', 'korean', 'french', 'indian']

headers = {
    'Content-Type': 'application/json',
}
