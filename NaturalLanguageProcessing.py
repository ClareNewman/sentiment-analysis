# Imports the Google Cloud client library
import math
import re

import numpy as np
import pandas as pd
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types


def clean_strings(statement):
    upper_statement = str(statement)
    upper_statement = upper_statement.upper()
    upper_statement = re.sub(r"[^\w\s]", "", upper_statement)

    print("Looking at:" + str(statement))

    if upper_statement in ["NO", "NA", "NONE", "NOTHING"]:
        return None
    else:
        return statement


def int_to_boolean(num):
    if not math.isnan(num):
        return bool(int(num))
    else:
        return None


def import_spreadsheet():
    rows_to_import = None

    csv = pd.read_csv("/Volumes/scLive/DATA 2018/LifePoint/HRD Survey Results/LifePoint Employee Survey 06092018.csv",
                      nrows=rows_to_import)

    csv = csv.rename(columns=lambda x: x.strip())

    # Trim down to the columns we are interested in
    csv = csv[
        ["Gender", "Do you have any children?", "Length of service (years)", "Job title",
         "Please select the facility in which you work.", "Can you tell us more?"]]

    csv["Gender"].astype("category")
    # print(csv.dtypes)
    # csv["Can you tell us more?"].astype

    # csv = csv["Do you have any children?"].apply(int_to_boolean)

    # csv = csv["Can you tell us more?"].apply(clean_strings)

    return csv


data = import_spreadsheet()

# Instantiates a client
client = language.LanguageServiceClient()

responses = data["Can you tell us more?"].values.tolist()

snippets = []

for response in responses:
    snippet = types.Document(content=str(response), type=enums.Document.Type.PLAIN_TEXT)
    analysis = client.analyze_sentiment(document=snippet)
    snippets.append(analysis)

sentiment = []

for snippet in snippets:
    for index, sentence in enumerate(snippet.sentences):
        sentiment.append(sentence.sentiment.score)
    # print("Sentiment of: {}\tfor sentence '{}'".format(round(sentence.sentiment.score, 2), sentence.text.content))

data["Can you tell us more? (sentiment)"] = pd.Series(sentiment)

gender = data.groupby("Gender")
print(gender["Can you tell us more? (sentiment)"].agg(np.mean))

children = data.groupby("Do you have any children?")
print(children["Can you tell us more? (sentiment)"].agg(np.mean))

location = data.groupby("Please select the facility in which you work.")
print(location["Can you tell us more? (sentiment)"].agg(np.mean))
