from variables import *  

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION_NAME)
table = dynamodb.Table(DYNAMO_DB_TABLE_NAME)

for cuisine_type in cuisine_types:
    offset = 0
    for i in range(0, 1):
        offset += 50
        PARAMETERS = {
            'term': 'restaurant',
            'location': 'New York',
            'radius': 40000,
            'categories': cuisine_type,
            'limit': 50,
            'offset': offset,
            'sort_by': 'best_match'
        }
        response = requests.get(url=ENDPOINT, params=PARAMETERS, headers=HEADERS)
        business_data = response.json()
        
        for biz in business_data['businesses']:
            try:
                table.put_item(
                    Item={
                        'businessId': biz['id'],
                        'name': biz['name'],
                        'category': biz['categories'][0]['alias'],
                        'address': biz['location']['address1'],
                        'city': biz['location']['city'],
                        'zipcode': biz['location']['zip_code'],
                        'latitude': Decimal(str(biz['coordinates']['latitude'])),
                        'longitude': Decimal(str(biz['coordinates']['longitude'])),
                        'reviewCount': biz['review_count'],
                        'rating': Decimal(str(biz['rating'])),
                        'phone': biz['phone'],
                        'url': str(biz['url']),
                        'insertedAtTimestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                )
            except ClientError as e:
                print(e.response['Error']['Code'])