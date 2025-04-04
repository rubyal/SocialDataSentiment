import boto3
import csv
import io
import os

s3 = boto3.client('s3')
comprehend = boto3.client('comprehend')

BUCKET_NAME = os.environ['BUCKET_NAME']
INPUT_FILE = os.environ['INPUT_FILE']
OUTPUT_FILE = os.environ['OUTPUT_FILE']

def analyze(event, context):
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=INPUT_FILE)
    data = obj['Body'].read().decode('utf-8')

    input_csv = csv.DictReader(io.StringIO(data), delimiter=';')
    output = io.StringIO()
    fieldnames = input_csv.fieldnames + ['Sentiment', 'Positive', 'Negative', 'Neutral', 'Mixed']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for row in input_csv:
        text = row['Text'].strip()
        if len(text) < 20:
            sentiment = {
                "Sentiment": "NEUTRAL",
                "SentimentScore": {
                    "Positive": 0,
                    "Negative": 0,
                    "Neutral": 1,
                    "Mixed": 0
                }
            }
        else:
            response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
            sentiment = response

        row['Sentiment'] = sentiment['Sentiment']
        row['Positive'] = sentiment['SentimentScore']['Positive']
        row['Negative'] = sentiment['SentimentScore']['Negative']
        row['Neutral'] = sentiment['SentimentScore']['Neutral']
        row['Mixed'] = sentiment['SentimentScore']['Mixed']
        writer.writerow(row)

    s3.put_object(Bucket=BUCKET_NAME, Key=OUTPUT_FILE, Body=output.getvalue())

    return {
        'statusCode': 200,
        'body': f'Sentiment analysis completed and saved to {OUTPUT_FILE}'
    }
