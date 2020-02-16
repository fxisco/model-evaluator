from django.shortcuts import render, redirect
from django.urls import reverse
from csv import reader
from urllib.parse import urlencode, unquote, parse_qs
from GetOldTweets3 import manager

from .forms import KeywordsForm
from .helpers import getValidKeywords


def index(request):
    form = KeywordsForm()

    if request.method == 'POST':
        form = KeywordsForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES['keywords'].read().decode("utf-8")
            lines = csv_file.splitlines()
            limited_lines = lines[0:10]
            cleaned_lines = [getValidKeywords(x) for x in limited_lines if x]

            return redirect(evaluate, keywords=urlencode({'keywords': ','.join(cleaned_lines)}))

    return render(request, 'keywords.html', { "form": form })

def evaluate(request, keywords):
    decoded_keywords = unquote(keywords) if keywords else []
    parsed_string = parse_qs(decoded_keywords)['keywords'][0]
    keywords_parsed = parsed_string.split(',')
    query = ' OR '.join(keywords_parsed)

    tweetCriteria = manager\
        .TweetCriteria()\
        .setQuerySearch(query)\
        .setLang("it")\
        .setMaxTweets(10)
    tweets = manager.TweetManager.getTweets(tweetCriteria)

    data = {
        "keywords": keywords_parsed,
        "tweets": tweets
    }


    return render(request, 'evaluator.html', { "data": data })
