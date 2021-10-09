# Dining-Concierge-Chatbot

## Overview

In this project I have implement a serverless, microservice-driven web application. Specifically, I have build a Dining Concierge chatbot that sends you restaurant suggestions given a set of preferences that you provide the chatbot with through conversation.


## Architecture

<img width="929" alt="Assignment 1 architecture diagram (2)" src="https://user-images.githubusercontent.com/85689959/136675790-24f28e24-45d6-4df2-85e0-4956405b6f88.png">


## Following points decribe how the project has been implemented:

1. The frontend is written in JavaScript and is hosted on AWS S3 bucket.
2. The API for the application has been setup Using AWS API Gateway.
3. A Lambda function (LF0) performs the chat operation using the request/response model (interfaces) specified in the API specification. When the API receives a request, it:
  ● Extracts the text message from the API request, 
  ● Sends it to the Lex chatbot, 
  ● Waits for the response, 
  ● Sends back the response from Lex as the API response.
4. The Dining Concierge chatbot is build using Amazon Lex with the following functionalities:
  ● GreetingIntent
  ● ThankYouIntent
  ● DiningSuggestionsIntent
5. For the DiningSuggestionsIntent, the following info is collected from the user:
  ● Location
  ● Cuisine
  ● Dining Time
  ● Number of people
  ● Phone number/Email ID
  Based on the parameters collected from the user (location, cuisine, etc.) this info is pushed to an SQS queue (Q1).
6. The Lambda function (LF1) acts as a code hook for Lex, which essentially entails the invocation of the Lambda before Lex responds to any of the requests which allows the manipulation and validation of parameters as well as formatting the bot’s responses and notifying the user that their request has been received and will be sent over SMS/EMail once the list of restaurant suggestions is ready.
7. The data for different restaurants (Business ID, Name, Address, Coordinates, Number of Reviews, Rating, Zip Code)is collected using the Yelp API and is stored in a DynamoDB table named “yelp-restaurants”.
8. Using the AWS ElasticSearch Service an index “restaurants” is created to store partial information (RestaurantID and Cuisine) for each restaurant.
9. A third Lambda function (LF2) (a suggestions module, that is decoupled from the Lex chatbot) acts as a queue worker. Whenever it is invoked it 
 ● Pulls a message from the SQS queue (Q1)
 ● Gets a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch and DynamoDB, 
 ● Formats them
 ● Sends them over text message to the phone number included in the SQS message, using SNS/SES
10. Lastly a CloudWatch event trigger is created that runs every minute and invokes the Lambda function automating the queue worker Lambda to poll and
process suggestion requests on its own. 

In summary, based on a conversation with the customer, the LEX chatbot will identify the customer’s preferred ‘cuisine’. It will search through ElasticSearch to get random 4/7suggestions of restaurant IDs with this cuisine. At this point, it will also query the DynamoDB table with these restaurant IDs to find more information about the restaurants to suggest to the customers like name and address of the restaurant.

