import re
import unidecode
import os
from unipath import Path
from uuid import uuid4
from weka.classifiers import Classifier, Evaluation
from weka.core.dataset import Attribute, Instance, Instances
import weka.core.converters as converters
import weka.core.jvm as jvm
import numpy as np

class_values = ["nega", "neut", "posi"]

def get_valid_keywords(text):
  unaccented_string = unidecode.unidecode(text)
  text_extra_spaces_removed = re.sub(' +', ' ', unaccented_string)
  new_word = re.sub('[^A-Za-z0-9# ]+', '', text_extra_spaces_removed)

  return new_word

def get_file_destinantion(filename):
  return Path(__file__).ancestor(3) + '/files_uploaded/' + filename

def get_test_filename(filename):
  return Path(__file__).ancestor(3) + '/tests_files/' + filename

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
  jvm.start()
  test_filename = get_test_filename('evento1.arff')
  data = converters.load_any_file(test_filename)
  data.class_is_last()
  classifier, _ = Classifier.deserialize(get_file_destinantion(filename))

  for index, inst in enumerate(data):
    pred = classifier.classify_instance(inst)
    dist = classifier.distribution_for_instance(inst)
    print(str(index+1) + ": label index=" + str(pred) + ", class distribution=" + str(dist))

  jvm.stop()

def create_dataset(tweets):
  jvm.start()
  text_att = Attribute.create_string('TEXT')
  nom_att = Attribute.create_nominal('CLASS', class_values)

  dataset = Instances.create_instances("tweets", [text_att, nom_att], 1)

  values = []
  values.append(dataset.attribute(0).add_string_value("blah de blah"))
  values.append(Instance.missing_value())
  inst = Instance.create_instance(values)
  dataset.add_instance(inst)

  dataset.class_is_last()

  print(dataset)
  jvm.stop()
