#!/usr/bin/env python3

import random
import sqlite3 as sqlite
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
from sklearn.metrics import classification_report
from common import *


def train(model, modelname):
    db = sqlite.connect(database)
    cursor = db.cursor()
    cursor.row_factory = lambda c, r: r[0]
    query = "SELECT text FROM Tweets WHERE airline_sentiment = '%s'"

    tweets = []
    tests = []
    classes = []
    testclasses = []
    testresults = []
    for c in classids:
        results = cursor.execute(query % classnames[c].lower()).fetchall()
        sample = random.sample(results, int(len(results) * 0.2))
        tweets += results
        tests += sample
        classes += [c] * len(results)
        testclasses += [c] * len(sample)

    cursor.close()
    db.close()

    model.fit(tweets, classes)

    for t in tests:
        testresults.append(model.predict([t])[0])

    print(modelname)
    print(classification_report(testclasses, testresults,
        target_names=classnames))


def main():
    nbmodel = Pipeline([
        ('vectorizer', TfidfVectorizer(preprocessor=tweet_preprocessor,
            stop_words=stopwords)),
        ('classifier', MultinomialNB())
        ])
    svmmodel = Pipeline([
        ('vectorizer', TfidfVectorizer(preprocessor=tweet_preprocessor,
            stop_words=stopwords)),
        ('classifier', LinearSVC(C=0.1))
        ])
    train(nbmodel, "Naive Bayes Classifier")
    train(svmmodel, "SVM Classifier")
    joblib.dump(nbmodel, nbfilename, compress=3)
    joblib.dump(svmmodel, svmfilename, compress=3)

if __name__ == '__main__':
    main()
