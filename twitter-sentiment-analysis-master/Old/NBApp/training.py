#!/usr/bin/env python3

from NB import Classifier
import sklearn.metrics
import os
import random
import joblib

def main():
    classifier = Classifier('../data/', './stop.txt')
    classlist = classifier.get_classes()
    classobj = list(classifier.doc_class)
    classnames = ['Positive', 'Neutral', 'Negative']
    y_true = list()
    y_pred = list()
    for c in classlist:
        dir = os.path.join('../data/', c)
        files = random.sample(os.listdir(dir),
                int(classifier.get_class_doc_count(c) * 0.2))
        for fn in files:
            predict = classifier.classify_document(os.path.join(dir, fn))
            y_true.append(int(c))
            y_pred.append(int(predict[1]))

    print(sklearn.metrics.classification_report(y_true, y_pred, target_names=classnames))
    joblib.dump(classifier, 'NBClassifier.pkl')

if __name__ == '__main__':
    main()
