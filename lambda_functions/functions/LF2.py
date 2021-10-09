from lf_variables import * 

def lambda_handler(event, context):
    try:
        sqs_client = boto3.client("sqs", region_name="us-east-1")
    except Exception as e:
        print(e)
    queue_url = QUEUE_URL
    try:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )
        message = response['Messages'][0]
        message_atributes = message['MessageAttributes']    
        cuisine = message_atributes['cuisine_type']
        cuisine_type = cuisine['StringValue']   
        loc = message_atributes['location']
        location = loc['StringValue'] 
        nop = message_atributes['number_of_people']
        number_of_people = nop['StringValue']  
        pn = message_atributes['phone_number']
        phone_number = pn['StringValue']  
        t1 = message_atributes['time']
        time = t1['StringValue']     
        restaurant_info = ""
        for i in range(1, 4):
            restaurantId = get_random_business_id(cuisine_type)
            restaurant_info += get_restaurant_info(restaurantId) + '\n' + '\n'
        print('Hello! Here are my '+ cuisine_type +' restaurant suggestions for ' + number_of_people + ' people, at ' + time + " " + '\n' +restaurant_info)
        sendMessage = 'Hello! Here are my '+ cuisine_type +' restaurant suggestions for ' + number_of_people + ' people, at ' + time + " " + '\n' +restaurant_info
        send_plain_email(sendMessage)
    except Exception as e:
        print(e)


def get_random_business_id(cuisine_type):
    http = urllib3.PoolManager()
    es_query = ES_QUERY.format(
        cuisine=cuisine_type,
        size_limit=3
        )
    http = urllib3.PoolManager()
    headers = urllib3.make_headers(basic_auth='prateek:Prateek@1709')
    response = http.request('GET', es_query, headers=headers)
    result = json.loads(response.data.decode('utf-8'))
    random_num_list = list(range(3))
    random.shuffle(random_num_list)
    for random_number in random_num_list:
        if result['hits']['hits'][random_number]['_source']['businessId'] != None:
            businessId = result['hits']['hits'][random_number]['_source']['businessId']
    return businessId


def get_restaurant_info(businessId):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMO_DB_TABLE_NAME)
    response = table.get_item(
        Key={
            'businessId': businessId
        }
    )
    response_item = response.get("Item")
    restaurant_name = response_item['name']
    restaurant_category = response_item['category']
    restaurant_address = response_item['address']
    restaurant_city = response_item['city']
    restaurant_zipcode = response_item['zipcode']
    restaurant_rating = str(response_item['rating'])
    restaurant_url = str(response_item['url'])
    restaurant_phone = response_item['phone']
    formatted_restaurant_info = (restaurant_name+" "+restaurant_address)
    return formatted_restaurant_info

    
def send_plain_email(sendMessage):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    ses_client.send_email(
        Destination={
            "ToAddresses": [
                "pk2460@nyu.edu",
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": sendMessage,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "Dining Concierge Chatbot",
            },
        },
        Source="pk2460@nyu.edu",
    )