from django.shortcuts import render, redirect
from django.urls import reverse
from csv import reader
from urllib.parse import urlencode, unquote, parse_qs

from .forms import KeywordsForm
from .helpers import getValidKeywords


def index(request):
    errors = []

    if request.method == 'POST':
        form = KeywordsForm(request.POST)

        if form.is_valid():
            words = form.cleaned_data.get('keywords')
            cleaned_keywords = getValidKeywords(words)

            # query_string =  urlencode({'keywords': ','.join(cleaned_keywords)})
            # url = '{}?{}'.format('evaluate', query_string)

            # print("URL:::" + url)
            return redirect(evaluate, keywords=urlencode({'keywords': ','.join(cleaned_keywords)}))
        else:
            errors.append('Should not be empty')

    data = {
        "errors": errors
    }

    return render(request, 'keywords.html', { "data": data })

def evaluate(request, keywords):
    errors = []
    decoded_keywords = unquote(keywords) if keywords else []
    parsed_string = parse_qs(decoded_keywords)['keywords'][0]
    print(parsed_string)

    data = {
        "keywords": parsed_string.split(','),
        "errors": errors
    }


    return render(request, 'evaluator.html', { "data": data })
