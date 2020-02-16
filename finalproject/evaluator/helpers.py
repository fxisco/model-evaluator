import re
import unidecode

def getValidKeywords(text):
  unaccented_string = unidecode.unidecode(text)
  text_extra_spaces_removed = re.sub(' +', ' ', unaccented_string)
  new_word = re.sub('[^A-Za-z0-9# ]+', '', text_extra_spaces_removed)

  return new_word
