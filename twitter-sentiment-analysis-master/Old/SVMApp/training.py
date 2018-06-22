#!/usr/bin/env python3
#Credit for SVM Algorith to Devika Kakkar

import csv
import os
import re
import nltk
import scipy
import sklearn.metrics
import sentiment
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.externals import joblib
from sklearn.pipeline import Pipeline
from sklearn.cross_validation import train_test_split

#Generating the Training and testing vectors

def getTrainingAndTestData():
    X = []
    y = []
    classes = [0,1,2]
    #data_dir = 'E:/Projects/Natural Language Processing/SVM/SVMApp/SVMApp/txt_sentoken/'
    data_dir = '../data/'
    for curr_class in classes:
            dirname = os.path.join(data_dir, str(curr_class))
            for fname in os.listdir(dirname):
                with open(os.path.join(dirname, fname), 'r') as f:
                    content = f.read()
                    if fname.startswith('cv8' or 'cv9'):
                        X.append(content)
                        y.append(curr_class)
                    else:
                        X.append(content)
                        y.append(curr_class)

    X_train, X_test, y_train, y_test = sklearn.cross_validation.train_test_split(X,y,test_size=0.20, random_state=42)
    return X_train, X_test, y_train, y_test

#Process Tweets (Stemming+Pre-processing)

def processTweets(X_train, X_test):
        X_train = [sentiment.stem(sentiment.preprocessTweets(tweet)) for tweet in X_train]
        X_test = [sentiment.stem(sentiment.preprocessTweets(tweet)) for tweet in X_test]
        return X_train,X_test
        
# SVM classifier

def classifier(X_train,y_train):
        print(y_train)
        vec = TfidfVectorizer(min_df=5, max_df=0.95, sublinear_tf = True,use_idf = True,ngram_range=(1, 2))
        svm_clf =svm.LinearSVC(C=0.1)
        vec_clf = Pipeline([('vectorizer', vec), ('pac', svm_clf)])
        vec_clf.fit(X_train,y_train)
        joblib.dump(vec_clf, 'svmClassifier.pkl', compress=3)
        return vec_clf


def main():
        X_train, X_test, y_train, y_test = getTrainingAndTestData()
        X_train, X_test = processTweets(X_train, X_test)
        vec_clf = classifier(X_train,y_train)
        y_pred = vec_clf.predict(X_test)
        classnames = ['Positive', 'Neutral', 'Negative']
        print(sklearn.metrics.classification_report(y_test, y_pred,
            target_names=classnames))  
        
if __name__ == "__main__":
    main()
