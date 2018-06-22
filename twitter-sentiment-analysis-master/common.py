import re
import nltk

# Data Definitions
classids = [0, 1, 2]
classnames = ['Positive', 'Neutral', 'Negative']
database = './database.sqlite'
nltk.data.path.append('./nltk_data')
stopwords = ['__url', '__handl'] + nltk.corpus.stopwords.words('english')

# Classifier Pickle Files
svmfilename = 'svmClassifier.pkl'
nbfilename = 'nbClassifier.pkl'

def tweet_preprocessor(string):
    '''
    Preprocess Tweets a bit to remove useless bits
    Based on Mike's preprocessTweets functions
    '''
    # replace urls with __url
    string = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+))', '__url', string)
    # replace twitter handles (@string) with __handle
    string = re.sub(r'@\S+', '__handle', string)
    # replace hashtags with normal words
    string = re.sub(r'#(\S+)', r'\1', string)
    # replace emoticons with __positive__ or __negative__, depending on type
    # I'm trusting Mike on this one (The regexes is the escaped versions of
    # these)
    # __positive__ = [':-)', ':)', '(:', '(-:', ':-D', ':D', 'X-D', 'XD', 'xD',
    #        '<3', ':\*', ';-)', ';)', ';-D', ';D', '(;', '(-;']
    # __negative__ =  [':-(', ':(', '(:', '(-:', ':,(', ':\'(', ':"(', ':((']
    string = re.sub(r'\:\-\)|\:\)|\(\:|\(\-\:|\:\-D|\:D|X\-D|XD|xD|\<3' \
        '|\:\\\*|\;\-\)|\;\)|\;\-D|\;D|\(\;|\(\-\;', '__positive__', string)
    string = re.sub(r'\:\-\(|\:\(|\(\:|\(\-\:|\:\,\(|\:\'\(|\:\"\(|\:\(\(',
        '__negative__', string)

    # Finally, run the string through a stemmer to remove morphological affixes
    stemmer = nltk.stem.SnowballStemmer('english')
    string = ' '.join([stemmer.stem(word) for word in string.split()])
    return string
