from datetime import datetime, timedelta
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from src.firebase import ReviewController
from collections import Counter
from src.model import Review
import requests
import nltk

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

stopwords = stopwords.words('english')
lematizer = WordNetLemmatizer()

tokenizer = AutoTokenizer.from_pretrained("avichr/heBERT_sentiment_analysis")

model = AutoModelForSequenceClassification.from_pretrained(
    "./resources/model"
)

sentiment_analysis = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    return_all_scores=True
)

review_controller = ReviewController()

app = Flask(__name__)

# Set CORS to be able to access from all origins
CORS(app)


@app.route("/")
def welcome():
    return "Hello Welcome"


@app.route("/predict", methods=['POST'])
def predict_sentiment():
    if request.method == 'POST':
        return jsonify(sentiment_analysis(request.form.get('text', default="")))
    else:
        return Response("/predict endpoint only support POST method", 405)


@app.route("/stt", methods=['POST'])
def speechToText():
    if request.method == 'POST':
        blob_url = request.form['blobUrl'].split(":", maxsplit=1)[-1]
        print(blob_url)
        data = requests.get(blob_url)
        print(data.content)
        return {}
    else:
        return Response("/predict endpoint only support POST method", 405)


@app.route("/analysis", methods=['GET'])
def getReviewAnalysis():
    stop = datetime.now()  # + timedelta(days=4)
    start = datetime(stop.year, stop.month, stop.day)

    reviews_per_day: list[list[Review]] = []

    for _ in range(7):

        reviews_per_day.append(
            review_controller.getReviewsInRange(start, stop)
        )

        stop = start
        start = start - timedelta(days=1)

    counts_per_day = [len(reviews) for reviews in reviews_per_day]

    total = sum(counts_per_day)

    average_sentiment = {
        'pos': 0.00,
        'neg': 0.00,
        'neu': 0.00,
    }

    sentiment_distribution_per_day = {
        'pos': [0.00] * 7,
        'neg': [0.00] * 7,
        'neu': [0.00] * 7,
    }

    negative_words = []
    positive_words = []

    def preprocess_text(text: str):
        text = text.lower()

        return [lematizer.lemmatize(x) for x in word_tokenize(text)
                if (len(x) > 2 and x not in stopwords)]

    for i in range(7):
        for review in reviews_per_day[i]:
            if review.highestLabel == "pos":
                positive_words += preprocess_text(review.text)
            elif review.highestLabel == "neg":
                negative_words += preprocess_text(review.text)
            else:
                pass

            score = review.sentimentScore.toMap()

            for key, val in score.items():
                sentiment_distribution_per_day[key][i] += val
                average_sentiment[key] += val

        for key in sentiment_distribution_per_day.keys():
            if sentiment_distribution_per_day[key][i] != 0:
                sentiment_distribution_per_day[key][i] /= counts_per_day[i]

    for key in average_sentiment.keys():
        if average_sentiment[key] != 0:
            average_sentiment[key] /= total

    neg_count = list(Counter(negative_words).most_common(15))
    pos_count = list(Counter(positive_words).most_common(15))

    return {
        "total_reviews": total,
        "reviews": [[review.toMap() for review in reviews] for reviews in reviews_per_day],
        "counts_per_day": counts_per_day,
        "average_sentiment": average_sentiment,
        "sentiment_distribution_per_day": sentiment_distribution_per_day,
        "pos_count": pos_count,
        "neg_count": neg_count,
    }
