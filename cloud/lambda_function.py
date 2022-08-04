# Lambda function that to send SNS informing user when logs are uploaded into the S3 bucket.
# This lambda function will be triggered when an object is created in the specific S3 bucket.
# Bucket must have been created and a trigger configured to call this lambda function when an ObjectCreate API call is performed on the bucket.



import json
import boto3
import logging

def lambda_handler(event, context):
        sns = boto3.client('sns')
        arn = 'arn of your AWS SNS' # Your arn should be the arn of the particular
        notification = f'pymetrics: System report logs have been uploaded into your S3 bucket'

        response = sns.publish(
            TargetArn = arn,
            Message = json.dumps({'default': notification}),
            MessageStructure = 'json'
            )

        return {
            'statusCode': 200,
            'body': json.dumps(response)

        }
