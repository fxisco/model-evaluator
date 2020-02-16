import re
import unidecode

def getValidKeywords(text):
  words = text.split(',')
  valid_keywords = []

  for word in words:
    unaccented_string = unidecode.unidecode(word)
    new_word = re.sub('[^A-Za-z0-9#]+', '', unaccented_string)
    valid_keywords.append(new_word)

  return valid_keywords
