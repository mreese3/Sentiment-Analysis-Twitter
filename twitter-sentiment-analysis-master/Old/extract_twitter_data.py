import tweepy    #this will give an error if tweepy is not installed properly
from tweepy import OAuthHandler
 
#provide your access details below 
access_token = "802201351707037696-4BHP7l7eT3FO59C42y61RDPPu3p5wbL"
access_token_secret = "3tL5GSLu1HFYOFoqf279H3OXxh3XgKiITZflTukmTpOjo"
consumer_key = "FH4OGYr4sdNWfgHqo5aRcRQeP"
consumer_secret = "J2w0aewZkcvUUIN74t9JKRbMGGmlxDDXyx1vQGIZlVC9QbOxS3"
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
api = tweepy.API(auth)    
    
from tweepy import Stream
from tweepy.streaming import StreamListener
count = 0;
class MyListener(StreamListener):
    
    def on_status(self, status):
        if hasattr(status, 'retweeted_status'): 
            return True
        else:
            try:
                with open('C:\\Users\\Yuffiek133\\Desktop\\Tweets\\python.json', 'a') as f:  #change location here
                    f.write(status.text + "\n\n\n")
                    print("Tweet Recorded:\n\n" + status.text)
                    return True
            except BaseException as e:
                print("Error on_data: %s" % str(e))
            return True
 
    def on_error(self, state):
        print(state)
        return True
 
twitter_stream = Stream(auth, MyListener())

#change the keyword here
twitter_stream.filter(track=['@Delta', '@AmericanAir', '@SouthwestAir', '@VirginAmerica', '@USAirways'])