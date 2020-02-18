import re
import unidecode
import os
from unipath import Path
from uuid import uuid4
from weka.classifiers import Classifier, Evaluation
from weka.core.dataset import Attribute, Instance, Instances
from weka.core.classes import list_property_names
import weka.core.converters as converters
import weka.core.jvm as jvm
import numpy as np

class_values = ["nega", "neut", "posi"]
RE_EMOJI = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
RE_LINKS = re.compile('^https?:\/\/.*[\r\n]*', flags=re.MULTILINE)

def get_valid_keywords(text):
  unaccented_string = unidecode.unidecode(text)
  text_extra_spaces_removed = re.sub(' +', ' ', unaccented_string)
  new_word = re.sub('[^A-Za-z0-9# ]+', '', text_extra_spaces_removed)

  return new_word

def get_file_destinantion(filename):
  return Path(__file__).ancestor(3) + '/files_uploaded/' + filename

def hangle_file_upload(file_uploaded):
  file_id = uuid4()
  filename =  str(file_id) + '.model'
  file_destination = get_file_destinantion(filename)

  with open(file_destination, 'wb+') as destination:
      for chunk in file_uploaded.chunks():
          destination.write(chunk)
      return filename

  return ''

def load_classification_model(filename):
  classifier, model = Classifier.deserialize(get_file_destinantion(filename))

  return {
    "classes": model.class_attribute.values,
    "classifier": classifier,
  }

def clean_tweet(tweet_text):
  cleaned_tweet = unidecode.unidecode(tweet_text)
  cleaned_tweet = re.sub('http\S+', '', cleaned_tweet)
  cleaned_tweet = re.sub(r"#(\w+)", '', cleaned_tweet, flags=re.MULTILINE)
  cleaned_tweet = re.sub(r"@(\w+)", '', cleaned_tweet, flags=re.MULTILINE)
  cleaned_tweet = re.sub('[^A-Za-z0-9 ]+', '', cleaned_tweet)
  cleaned_tweet = re.sub(' +', ' ', cleaned_tweet.strip())

  return cleaned_tweet

def get_cleaned_tweets(tweets):
  result = []

  for tweet in tweets:
    result.append(clean_tweet(tweet.text))

  return result

def create_dataset(tweets):
  text_att = Attribute.create_string('TEXT')
  nom_att = Attribute.create_nominal('CLASS', class_values)
  dataset = Instances.create_instances("tweets", [text_att, nom_att], len(tweets))

  for tweet in tweets:
    values = []
    values.append(dataset.attribute(0).add_string_value(tweet))
    values.append(Instance.missing_value())
    inst = Instance.create_instance(values)
    dataset.add_instance(inst)

  dataset.class_is_last()

  return dataset

def evaluate_model_and_testset(model, testset):
  predictions = []

  for index, inst in enumerate(testset):
    pred = model['classifier'].classify_instance(inst)
    predictions.append(model['classes'][int(pred)])

  return predictions

