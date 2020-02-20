from django.shortcuts import render, redirect
from django.urls import reverse
from csv import reader
from urllib.parse import urlencode, unquote, parse_qs
from GetOldTweets3 import manager
import weka.core.jvm as jvm
from datetime import datetime, timedelta
from os import path

from .forms import KeywordsForm
from .helpers import get_valid_keywords, hangle_file_upload, load_classification_model,create_dataset,evaluate_model_and_testset,get_cleaned_tweets, get_file_destinantion, generate_random_colors, get_value_of_classes, get_predictions_colors

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
                'filename': file_uploaded,
                'quantity': form.cleaned_data.get('quantity'),
                'startdate': form.cleaned_data.get('startdate'),
                'enddate': form.cleaned_data.get('enddate'),
                'language': form.cleaned_data.get('language'),
            }

            return redirect(evaluate, data=urlencode(data))

    return render(request, 'keywords.html', { "form": form })

def evaluate(request, data):
    decoded_data = unquote(data) if data else []
    parsed_keys = parse_qs(decoded_data)
    parsed_string = parsed_keys['keywords'][0]
    filename = parsed_keys['filename'][0]
    quantity = int(parsed_keys['quantity'][0])
    startdate = parsed_keys['startdate'][0]
    enddate = parsed_keys['enddate'][0]
    language = parsed_keys['language'][0]
    file_location = get_file_destinantion(filename)

    if not path.exists(file_location):
        return render(request, 'model_not_found.html')

    keywords_parsed = parsed_string.split(',')
    query = ' OR '.join(keywords_parsed)
    tweets = []

    jvm.start()

    model = load_classification_model(filename)

    tweetCriteria = manager\
        .TweetCriteria()\
        .setQuerySearch(query)\
        .setSince(startdate)\
        .setUntil(enddate)\
        .setLang(language)\
        .setMaxTweets(quantity)
    tweets = manager.TweetManager.getTweets(tweetCriteria)
    cleaned_tweets = get_cleaned_tweets(tweets)
    dataset = create_dataset(cleaned_tweets)

    predictions = evaluate_model_and_testset(model, dataset)

    jvm.stop()

    labels = model['classes']
    values = get_value_of_classes(model['classes'], predictions)
    fill_color = generate_random_colors(model['classes'])
    predictions_colors = get_predictions_colors(predictions, model['classes'], fill_color)

    data = {
        "keywords": keywords_parsed if keywords_parsed else [],
        "tweets": zip(tweets, cleaned_tweets, predictions, predictions_colors),
        "size": len(tweets),
        "labels": labels,
        "values": values,
        "fill_color": fill_color,
    }

    return render(request, 'evaluator.html', { "data": data })
