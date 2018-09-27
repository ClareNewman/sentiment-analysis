# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import pandas as pd
import numpy as np
# import os

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"

# Instantiates a client
client = language.LanguageServiceClient()

csv = pd.read_csv("/Volumes/scLive/DATA 2018/LifePoint/HRD Survey Results/LifePoint Employee Survey 06092018.csv")
#                  nrows=25)

csv = csv.rename(columns=lambda x: x.strip())
# print(type(csv.to_string(columns=["Can you tell us more?"])))

# with open('Advocacy_short.csv', 'r') as free_text:
#    responses = []
#    for response in free_text:
#        responses.append(response)

# responses = ["This is good", "I hate this", "It's OK"]

responses = csv["Can you tell us more?"].values.tolist()
# responses = [x for x in responses if str(x) != "nan"]
# print(responses)

snippets = []
analysis = ""

for response in responses:
    snippet = types.Document(content=str(response), type=enums.Document.Type.PLAIN_TEXT)
    analysis = client.analyze_sentiment(document=snippet)
    snippets.append(analysis)

sentiment = []

for snippet in snippets:
    for index, sentence in enumerate(snippet.sentences):
        sentiment.append(sentence.sentiment.score)
#       print("Sentiment of: {}\tfor sentence '{}'".format(round(sentence.sentiment.score, 2), sentence.text.content))

csv["Can you tell us more? (sentiment)"] = pd.Series(sentiment)
csv = csv.drop("#", 1)
csv["Gender"].astype("category")

tell_us_more = csv[["Gender", "Do you have any children?", "Can you tell us more?", "Can you tell us more? (sentiment)"]]
gender = tell_us_more.groupby("Gender")
print(gender["Can you tell us more? (sentiment)"].agg(np.mean))
children = tell_us_more.groupby("Do you have any children?")
print(children["Can you tell us more? (sentiment)"].agg(np.mean))

# print(csv.columns.values)
# print(tell_us_more.head())
# print(csv.shape)
