from django.shortcuts import render, redirect
from django.urls import reverse
from csv import reader
from urllib.parse import urlencode, unquote, parse_qs
from GetOldTweets3 import manager

from .forms import KeywordsForm
from .helpers import get_valid_keywords, hangle_file_upload, load_classification_model,create_dataset

def index(request):
    form = KeywordsForm()

    if request.method == 'POST':
        form = KeywordsForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES['keywords'].read().decode("utf-8")
            lines = csv_file.splitlines()
            limited_lines = lines[0:10]
            cleaned_lines = [get_valid_keywords(x) for x in limited_lines if x]
            file_uploaded = hangle_file_upload(request.FILES['model'])
            data = {
                'keywords': ','.join(cleaned_lines),
                'filename': file_uploaded
            }

            return redirect(evaluate, data=urlencode(data))

    return render(request, 'keywords.html', { "form": form })

def evaluate(request, data):
    decoded_data = unquote(data) if data else []
    parsed_keys = parse_qs(decoded_data)
    parsed_string = parsed_keys['keywords'][0]
    filename = parsed_keys['filename'][0]
    keywords_parsed = parsed_string.split(',')
    query = ' OR '.join(keywords_parsed)
    tweets = []
    # load_classification_model(filename)

    tweetCriteria = manager\
        .TweetCriteria()\
        .setQuerySearch(query)\
        .setLang("it")\
        .setMaxTweets(10)
    tweets = manager.TweetManager.getTweets(tweetCriteria)
    create_dataset(tweets)
    tweets = tweets if tweets else []

    data = {
        "keywords": keywords_parsed if keywords_parsed else [],
        "tweets": tweets
    }

    return render(request, 'evaluator.html', { "data": data })
