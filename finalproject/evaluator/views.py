from django.shortcuts import render, redirect
from django.urls import reverse
from csv import reader
from urllib.parse import urlencode, unquote, parse_qs
from GetOldTweets3 import manager
import weka.core.jvm as jvm
from datetime import datetime, timedelta

from .forms import KeywordsForm
from .helpers import get_valid_keywords, hangle_file_upload, load_classification_model,create_dataset,evaluate_model_and_testset,get_cleaned_tweets

def index(request):
    form = KeywordsForm()

    if request.method == 'POST':
        form = KeywordsForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            csv_file = request.FILES['keywords'].read().decode("utf-8")
            lines = csv_file.splitlines()
            limited_lines = lines[0:10]
            cleaned_lines = [get_valid_keywords(x) for x in limited_lines if x]
            file_uploaded = hangle_file_upload(request.FILES['model'])
            data = {
                'keywords': ','.join(cleaned_lines),
                'filename': file_uploaded,
                'quantity': request.POST['quantity'],
                'date': request.POST['date']
            }

            return redirect(evaluate, data=urlencode(data))

    return render(request, 'keywords.html', { "form": form })

def evaluate(request, data):
    decoded_data = unquote(data) if data else []
    parsed_keys = parse_qs(decoded_data)
    parsed_string = parsed_keys['keywords'][0]
    filename = parsed_keys['filename'][0]
    quantity = int(parsed_keys['quantity'][0])
    date = parsed_keys['date'][0]
    date_parsed = datetime.strptime(date, '%Y-%m-%d')
    next_date = date_parsed + timedelta(days=1)

    keywords_parsed = parsed_string.split(',')
    query = ' OR '.join(keywords_parsed)
    tweets = []

    jvm.start()

    model = load_classification_model(filename)

    tweetCriteria = manager\
        .TweetCriteria()\
        .setQuerySearch(query)\
        .setSince(date)\
        .setUntil(str(next_date.date()))\
        .setLang("it")\
        .setMaxTweets(quantity)
    tweets = manager.TweetManager.getTweets(tweetCriteria)
    cleaned_tweets = get_cleaned_tweets(tweets)
    dataset = create_dataset(cleaned_tweets)

    predictions = evaluate_model_and_testset(model, dataset)

    jvm.stop()

    data = {
        "keywords": keywords_parsed if keywords_parsed else [],
        "tweets": zip(tweets, cleaned_tweets, predictions),
        "size": len(tweets),
    }

    return render(request, 'evaluator.html', { "data": data })
