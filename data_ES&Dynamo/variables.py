import boto3
import datetime
import requests
import json, os
from decimal import Decimal
from datetime import datetime
from elasticsearch import Elasticsearch
from botocore.exceptions import ClientError

API_KEY = 'g90aWZAKlnXpydx_-9kbX5b0TvvThxKi0kR0LvF4vYAiItIlSjNswiywHhFcKlTusp-Iz-6GTBCHInwzSJyLx9SCWbvaznobu9moPUMTn-hdovAWKiVavkn8RV1TYXYx'
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

ES_USER = 'prateek'
ES_PASS = 'Prateek@1709'
ES_URL = 'https://search-restaurants-tjdy4o57veqr6t73mf4rgl4o44.us-east-1.es.amazonaws.com/restaurants/Restaurant/{count}'

DYNAMO_DB_TABLE_NAME = 'yelp-restaurants'

AWS_REGION_NAME = 'us-east-1'

cuisine_types = ['carribean' , 'turkish', 'peruvian', 'vietnamese','turkish', 'greek', 'thai', 'chinese', 'italian', 'mexican', 'japanese', 'korean', 'french', 'indian']

headers = {
    'Content-Type': 'application/json',
}