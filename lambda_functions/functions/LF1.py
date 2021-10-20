import json
import datetime
import time
import dateutil.parser
import logging
import boto3
import re
import os
#from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    print("Debug: Session attr: ",session_attributes)
    if not message['content']:
        return {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ElicitSlot',
                'intentName': intent_name,
                'slots': slots,
                'slotToElicit': slot_to_elicit
            }
        }
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---

def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.
    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


# --------------------- Validation driver function ---------------------

def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

# --------------------- Validation functions for each slot ---------------------

def isvalid_location(location):
    locations = ['manhattan', 'brooklyn', 'queens', 'sunset park', 'egewater', 'bensonhurst', 'jackson heights', 'union city', 'fairview', 'crown heights', 'staten island', 'astoria', 'sunnyside', 'long island city']
    if not location:
        return build_validation_result(False,
                               'Location',
                               '')
    if location.lower() not in locations:
        return build_validation_result(False,
                                       'Location',
                                       'We do not serve this area right now. Please try another location in NYC')
    return build_validation_result(True,'','')

def isvalid_cuisine(cuisine):
    if not cuisine :
        return build_validation_result(False,
                                       'Cuisine',
                                       '')
    cuisines = ['indian','thai','american','chinese','italian','mexican']
    if cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'Cuisine',
                                       'This cuisine is not available')
    print("Debug: cuisine is: ",cuisine)
    return build_validation_result(True,'','')
    
def isvalid_time(time):
    print("Debug: time is:",time)
    if not time:
        return build_validation_result(False,'BookingTime','')
    #nowe = datetime.datetime.now()
    #now1=datetime.datetime.strptime(nowe, '%H:%M')
    now = datetime.datetime.now()
    noww = now.strftime("%H:%M")
    time2=datetime.datetime.strptime(time, '%H:%M')
    print(time2)
    print('now',noww)
    if time<noww:  
        return build_validation_result(False,'BookingTime','Please enter a Dining Time which is after current time')
    return build_validation_result(True,'','')

def isvalid_date(date):
    print("Debug: Date is:",date)
    if not date:
        return build_validation_result(False,'BookingDate','')
    past = datetime.datetime.strptime(date, '%Y-%m-%d')
    present = datetime.datetime.now()
    if past.date() < present.date():
        return build_validation_result(False,'BookingDate','Dining Date cannot be older than Current Date')
    return build_validation_result(True,'','')

def isvalid_people(num_people):
    if not num_people:
         return build_validation_result(False,'NoOfPeople','')
    num_people = int(num_people)
    if num_people > 20:
        return build_validation_result(False,'NoOfPeople','Sorry, Only upto 20 people allowed')
    return build_validation_result(True,'','')

def isvalid_email(email):
    if not email:
        return build_validation_result(False, 'EMail', '')
    EMAIL_REGEX = re.compile(r"""(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#'$"""+r"""%&*+\/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d"""+r"""-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*"""+r"""[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4]["""+r"""0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|["""+r"""a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|"""+r"""\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")
    if not EMAIL_REGEX.match(email):
        return build_validation_result(False,'EMail','Please enter valid email address')
    return build_validation_result(True,'','')


def validate_reservation(restaurant):
    
    location = restaurant['Location']
    cuisine = restaurant['Cuisine']
    diningdate = restaurant['BookingDate']
    diningtime = restaurant['BookingTime']
    numberpeople = restaurant['NoOfPeople']
    email = restaurant['EMail']
    

    if not location or not isvalid_location(location)['isValid']:
        return isvalid_location(location)
    
    if not cuisine or not isvalid_cuisine(cuisine)['isValid']:
        return isvalid_cuisine(cuisine)
        
    if not diningdate or not isvalid_date(diningdate)['isValid']:
        return isvalid_date(diningdate)

    if not diningtime or not isvalid_time(diningtime)['isValid']:
        return isvalid_time(diningtime)
        
    if not numberpeople or not isvalid_people(numberpeople)['isValid']:
        return isvalid_people(numberpeople)
        
    if not email or not isvalid_email(email)['isValid']:
        return isvalid_email(email)
        
    # return True json if nothing is wrong
    return build_validation_result(True,'','')


def restaurantSQSRequest(requestData):
    
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/244220539866/Q1'
    delaySeconds = 5
    messageAttributes = {
        'cuisine': {
            'DataType': 'String',
            'StringValue': requestData['Cuisine']
        },
        'location': {
            'DataType': 'String',
            'StringValue': requestData['Location']
        },
        "time": {
            'DataType': "String",
            'StringValue': requestData['BookingTime']
        },
        "date": {
            'DataType': "String",
            'StringValue': requestData['BookingDate']
        },
        'numberpeople': {
            'DataType': 'Number',
            'StringValue': requestData['NoOfPeople']
        },
        'email': {
            'DataType' : 'String',
            'StringValue' : requestData['EMail']
        }
    }
    messageBody=('Recommendation for the food')
    
    response = sqs.send_message(
        QueueUrl = queue_url,
        DelaySeconds = delaySeconds,
        MessageAttributes = messageAttributes,
        MessageBody = messageBody
        )

    print("response", response)
    
    print ('send data to queue')
    print(response['MessageId'])
    
    return response['MessageId']

def make_restaurant_reservation(intent_request):
    """
    Performs dialog management and fulfillment for booking a hotel.
    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    print("Debug: Entered make_restaurant_reservation" )
    location = try_ex(lambda: intent_request['currentIntent']['slots']['Location'])
    print("Debug: Location is  ",location)
    cuisine = try_ex(lambda: intent_request['currentIntent']['slots']['Cuisine'])
    diningdate = try_ex(lambda: intent_request['currentIntent']['slots']['BookingDate'])
    diningtime = try_ex(lambda: intent_request['currentIntent']['slots']['BookingTime'])
    numberpeople = try_ex(lambda: intent_request['currentIntent']['slots']['NoOfPeople'])
    email = try_ex(lambda: intent_request['currentIntent']['slots']['EMail'])

    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # Load confirmation history and track the current reservation.
    reservationJson = json.dumps({
        'Location': location,
        'Cuisine': cuisine,
        'BookingDate': diningdate,
        'BookingTime': diningtime,
        'NoOfPeople': numberpeople,
        'EMail':email
    })
    reservation = json.loads(reservationJson)
    # session_attributes['currentReservation'] = reservation

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_reservation(reservation)
        print("Debug: Validation result is: ", validation_result)
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None
            print(elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            ))
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        # Otherwise, let native DM rules determine how to elicit for slots and prompt for confirmation.  Pass price
        # back in sessionAttributes once it can be calculated; otherwise clear any setting from sessionAttributes.
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

        print("output_session_attributes", output_session_attributes)
        
        # return delegate(output_session_attributes, intent_request['currentIntent']['slots'])
      
    requestData = {
                    'Location': location,
                    'Cuisine': cuisine,
                    'BookingDate': diningdate,
                    'BookingTime': diningtime,
                    'NoOfPeople': numberpeople,
                    'EMail':email
                }
                
    # print (requestData)
    
    
    messageId = restaurantSQSRequest(requestData)
    print ("Debug: messageId:",messageId)

    return close(intent_request['sessionAttributes'],
             'Fulfilled',
             {'contentType': 'PlainText',
              'content': 'I have received your request and will be sending the suggestions shortly. Have a Great Day !!'})

# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return make_restaurant_reservation(intent_request)
    elif intent_name == 'GreetingIntent':
        return greeting_intent(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thankyou_intent(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)

def greeting_intent(intent_request):
    
    return {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
              "contentType": "SSML",
              "content": "Hi there, how can I help?"
            },
        }
    }
    
def thankyou_intent(intent_request):
    
    return {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
              "contentType": "SSML",
              "content": "You’re welcome."
            },
        }
    }
