#!/usr/bin/env python3

# Show a bargraph

import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np
import random # generate random ints until tweetstream works
import time
import tweepy
import sys
from sklearn.externals import joblib
from common import *

# Twitter OAuth Keys
apikeys = {
        'consumer':"Gs8YOpll5farvSXb7BGc8eZUg",
        'consumer_secret': "iivoUY83vHLWxIEYIwkxgy3minKvkf0P0KnxBQ8baUaFXAEfYj",
        'token': "806663459450535942-3Afdy4eptONieYpU3QaPqGGdvdcvI1T",
        'token_secret': "9OsB4uJPqcnRfNatg7TiKShIVTdEA9polPdJo9gHnnhgF"
        }


colors = ['#6fc20f', '#c2bb0f', '#c2340f']
width = 0.8
xlocs = [0.4, 1.4, 2.4]
sentiment_names = ['Positive', 'Neutral', 'Negative']
svmsums = [0, 0, 0]
nbsums = [0, 0, 0]
figure, (svmgraph, nbgraph) = plt.subplots(nrows=2, gridspec_kw={'hspace': 0.5})
nbbars = nbgraph.bar(xlocs, nbsums, width, color=colors)
svmbars = svmgraph.bar(xlocs, svmsums, width, color=colors)
svmclass = joblib.load('SVMApp2/svmClassifier.pkl')
nbclass = joblib.load('NBApp2/nbClassifier.pkl')

def predict(string, classifier):
    string = preprocessTweet(string)
    if '__positive__' in string:
        return 0
    elif '__negative__' in string:
        return 2
    else:
        x = [string]
        return int(classifier.predict(x))

def animate_graph(i):
    pass


class NLPStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if hasattr(status, 'retweeted_status'):
            return True
        else:
            nbguess = nbclass.predict([status.text])[0]
            svmguess = svmclass.predict([status.text])[0]
            print('Tweet ID: %d\tSVM Guess: %s\tNB Guess: %s\n%s\n' %
                    (status.id, sentiment_names[svmguess],
                        sentiment_names[nbguess], status.text))

    def on_error(self, state):
        print(state)
        return True


def main():
    # Initialize Twitter Data
    tauth = tweepy.OAuthHandler(apikeys['consumer'],
            apikeys['consumer_secret'])
    tauth.set_access_token(apikeys['token'], apikeys['token_secret'])
    tapi = tweepy.API(tauth)
    tstream = tweepy.Stream(tapi.auth, NLPStreamListener())
    tstream.filter(track=['@united', '@AmericanAir', '@Delta',
        '@SouthwestAir'], async=True)

    # Setup Graph
    nbgraph.set_title('Naive Bayes Classification')
    nbgraph.set_ylabel('# of Tweets')
    nbgraph.set_ylim(bottom=0, top=1000, auto=True)
    nbgraph.set_xticks([x + width/2 for x in xlocs])
    nbgraph.set_xticklabels(tuple(sentiment_names))
    nbgraph.set_xlabel('Classification')

    svmgraph.set_title('SVM Classification')
    svmgraph.set_ylabel('# of Tweets')
    svmgraph.set_ylim(bottom=0, top=1000, auto=True)
    svmgraph.set_xticks([x + width/2 for x in xlocs])
    svmgraph.set_xticklabels(tuple(sentiment_names))
    svmgraph.set_xlabel('Classification')

    animation = anim.FuncAnimation(figure, animate_graph, interval=100)
    plt.show()
    print("NB totals: %s: %d\t%s: %d\t%s: %d" % (sentiment_names[0], nbsums[0],
        sentiment_names[1], nbsums[1], sentiment_names[2], nbsums[2]))
    tstream.disconnect()
    sys.exit(0)


if __name__ == '__main__':
    main()
