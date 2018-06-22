#!/usr/bin/env python3

import sys
import tweepy
import time
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sklearn.externals import joblib
from common import *
from apikeys import *
#from apikeys_backup import *

# Twitter Track Filter (Add terms to search here)
twitter_filter = [
        '@united',
        '@AmericanAir',
        '@Delta',
        '@SouthwestAir',
        '@VirginAmerica',
        '@VirginAtlantic',
        '@AlaskaAir',
        '@JetBlue',
        '@Allegiant',
        '@FlyFrontier',
        '@HawaiianAir',
        '@SpiritAirlines',
        '@KLM',     #Possible Non-English Starts Here
        '@SingaporeAir',
        '@lufthansa',
        ]

# Graph Configuration
bar_colors = ['#6fc20f', '#c2bb0f', '#c2340f']
bar_width = 0.8
bar_xlocs = [0.4, 1.4, 2.4]

# Collected Tweet Sums
nbsums = [0, 0, 0]
svmsums = [0, 0, 0]

# Loaded Models
nbmodel = joblib.load(nbfilename)
svmmodel =joblib.load(svmfilename)

# Twitter Stream
twitter_stream = None

# Analysis File
analysis_location = 'output'
analysis_file = None

class SentimentAnalysisStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if hasattr(status, 'retweeted_status'):
            return True
        else:
            nbguess = nbmodel.predict([status.text])[0]
            svmguess = svmmodel.predict([status.text])[0]
            nbsums[nbguess] += 1
            svmsums[svmguess] += 1
            current_time = time.strftime('%H:%M:%S,%Y-%m-%d')
            print(current_time + ": Total Tweets: %d" %
                    sum(nbsums))
            print("NB Guess: %s\tSVM Guess: %s\n%s\n" % (classnames[nbguess],
                classnames[svmguess], status.text))
            analysis_file.write("%s,%d,%d,%s\n" %
                    (current_time, nbguess, svmguess, status.text))

    def on_error(self, state):
        print(state)
        return True


def init_twitter():
    auth = tweepy.OAuthHandler(consumer_token, consumer_token_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    global twitter_stream
    twitter_stream = tweepy.Stream(api.auth, SentimentAnalysisStreamListener())
    twitter_stream.filter(track=twitter_filter, async=True)


def init_graph():
    fig = plt.figure()
    fig.canvas.set_window_title('Live Twitter Analysis - Started ' +
            time.strftime('%H:%M:%S %Y-%m-%d'))
    nbax = fig.add_subplot(2,1,1)
    svmax = fig.add_subplot(2,1,2)
    nbax.set_title('Naive Bayes Classifier')
    nbax.set_ylabel('# of Tweets')
    nbax.set_ylim(bottom=0, top=50)
    nbax.set_xticks([x + bar_width / 2 for x in bar_xlocs])
    nbax.set_xticklabels(tuple(["%s\n%d" % (n, c) for n, c in zip(classnames,
        nbsums)]))

    svmax.set_title('SVM Classifier')
    svmax.set_ylabel('# of Tweets')
    svmax.set_ylim(bottom=0, top=50)
    svmax.set_xticks([x + bar_width / 2 for x in bar_xlocs])
    svmax.set_xticklabels(tuple(["%s\n%d" % (n, c) for n, c in zip(classnames,
        svmsums)]))

    anim = animation.FuncAnimation(fig, animate_graph, interval=100,
            fargs=[fig])
    plt.tight_layout()
    plt.show()


def animate_graph(i, figure):
    nbax = figure.add_subplot(2,1,1)
    svmax = figure.add_subplot(2,1,2)
    if max(svmsums) > svmax.get_ylim()[1] or max(nbsums) > nbax.get_ylim()[1]:
        nbax.set_ylim(top=nbax.get_ylim()[1] * 2)
        svmax.set_ylim(top=svmax.get_ylim()[1] * 2)
    nbbars = nbax.bar(bar_xlocs, nbsums, bar_width, color=bar_colors)
    svmbars = svmax.bar(bar_xlocs, svmsums, bar_width, color=bar_colors)
    nbax.set_xticklabels(tuple(["%s\n%d" % (n, c) for n, c in zip(classnames,
        nbsums)]))
    svmax.set_xticklabels(tuple(["%s\n%d" % (n, c) for n, c in zip(classnames,
        svmsums)]))


def main():
    global analysis_file
    try:
        filename = os.path.join(analysis_location, 'predicition_output-%s.csv'
                % time.strftime('%H-%M-%S_%Y-%m-%d'))
        analysis_file = open(filename, mode='w', buffering=1)
        analysis_file.write("Time,Date,NB Guess,SVM Guess,Tweet Text\n")
    except IOError as e:
        raise IOError("Could not open analysis output file: %s" % e.strerror)
        sys.exit(1)

    init_twitter()
    init_graph()
    twitter_stream.disconnect()
    analysis_file.close()
    print("Naive Bayes Totals:")
    print("Positive: %d\tNeutral: %d\t Negative: %d\n" % tuple(nbsums))
    print("SVM Totals:")
    print("Positive: %d\tNeutral: %d\t Negative: %d\n" % tuple(svmsums))

if __name__ == '__main__':
    main()
