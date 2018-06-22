'''
Multinomial Naive Bayesian Document Classifier
'''

from collections import Counter
import os
import sys
import re
import math
from .tweetfix import preprocessTweet

class DocumentClass(object):
    '''
    Contains the individual document class information, such as word counts,
    vocab size, etc.
    '''
    def __init__(self, name):
        self.name = name
        self.wc = Counter()
        self.class_wc = 0
        self.doc_count = 0

    def addword(self, word):
        '''
        Add a word into the document class
        '''
        self.wc[word] += 1
        self.class_wc += 1

    def removeword(self, word):
        '''
        Try to remove a word from the document class
        '''
        if word in self.wc.keys():
            self.class_wc -= self.wc[word]
            self.wc.pop(word)

    def __getitem__(self, key):
        '''
        Let the word counts be accessed like a dict.
        '''
        return self.wc[key]

    def __len__(self):
        '''
        Make the len() calls return the word count
        '''
        return self.class_wc

    def __str__(self):
        '''
        Return the class name
        '''
        return self.name

    def doc_add(self):
        self.doc_count += 1

    def word_probability(self, word):
        return self.wc[word] / self.class_wc

class Classifier(object):
    '''
    Document Classifier
    '''
    # Different test regexes to use to tokenize training and testing files
    # Enable one
    #regex = re.compile('[A-Za-z0-9]+')  # Capture only Alphanumeric words
    #regex = re.compile('[A-Za-z]+')    # Capture Alphabet words only
    #regex = re.compile('\w+')          # Capture Alphanumeric + _ words
    #regex = re.compile('\w[\w\'+]\w+') # Capture words with apastrophes
    regex = re.compile('\S+')

    def __init__(self, trainingdir, stopfile=None):
        self.total_documents = 0
        self.doc_class = set()
        self.vocab = set()
        self._train(trainingdir)
        if (stopfile):
            self.stopwords = set()
            self._stoplist_build(stopfile)
        else:
            self.stopwords = None


    def _train(self, trainingdir):
        '''
        Build the document classifier training dataset
        Internal function
        '''

        # try to look into our training directory for class names
        try:
            for dclass in os.listdir(trainingdir):
                # Don't match dotfiles or other non-alpha named stuff
                if re.match('^\w+$', dclass):
                    self.doc_class.add(DocumentClass(dclass))

        except IOError as e:
            raise IOError('Could not open training directory (%s): %s' %
                    (trainingdir, e.strerror))

        # Now lets build our training set from the files in the class
        # directories
        for dclass in self.doc_class:
            dirname = os.path.join(trainingdir, dclass.name)
            try:
                for filename in os.listdir(dirname):
                    # Try to open each file and read, but do not fail if a file
                    # is unreadable, just print a warning
                    try:
                        with open(os.path.join(dirname, filename)) as doc:
                            self.total_documents += 1
                            dclass.doc_add()
                            for line in doc:
                                line = preprocessTweet(line)
                                # Quadruple for loops.  Great algorithmic
                                # efficiency here
                                for word in re.findall(Classifier.regex, line):
                                    dclass.addword(word)
                                    self.vocab.add(word)

                    except IOError as e:
                        print("Warning: Could not open file %s in %s: %s" %
                                (filename, dirname, e.strerror))

            except IOError as e:
                raise IOError("Could not open the document directory for" \
                        " class %s (%s): %s" % (dclass, dirname, e.strerror))


    def _stoplist_build(self, stopfile):
        '''
        Try to open the stopfile and add the words to our stoplist.
        Internal function
        '''
        try:
            with open(stopfile) as sf:
                for line in sf:
                    self.stopwords.add(line.rstrip('\n'))

            for dc in self.doc_class:
                for word in self.stopwords:
                    dc.removeword(word)

            for word in self.stopwords:
                if word in self.vocab:
                    self.vocab.discard(word)

        except IOError as e:
            print("Could not open stopfile %s: %s" % (stopfile, e.strerror))


    def classify_strings(self, strings):
        '''
        Classify the passed list of strings
        '''
        counter = Counter()
        for line in strings:
            for word in re.findall(Classifier.regex, line):
                counter[word] += 1

        if (self.stopwords):
            for word in self.stopwords:
                if word in counter.keys():
                    counter.pop(word)

        newvocab = set()
        for w in [x for x in counter.keys() if x not in self.vocab]:
            newvocab.add(w)

        vsize = len(newvocab) + len(self.vocab)

        p_dict = dict()

        for dc in self.doc_class:
            probability = 0.0
            for word in counter.keys():
                probability += math.log10((dc[word] + 1) / (len(dc) + vsize))
                #probability += math.log10(counter[word])
            probability += math.log10(dc.doc_count / self.total_documents)
            p_dict[dc.name] = probability

        chosen_class = max(p_dict, key=(lambda x: p_dict[x]))
        return (strings, chosen_class, p_dict)


    def predict(self, strings):
        '''
        Emulate SVMApp predictor code
        '''
        return self.classify_strings(strings)[1]


    def classify_document(self, documentname):
        '''
        Open the file to classify and preform classification
        Arguments:
            -documentname: string containing document to open

        Returns a tuple consisting of (documentname, chosen_class, {classname: prob, ...})
        '''
        ret = ('','',dict())
        try:
            with open(documentname) as doc:
                ret = self.classify_strings(doc.readlines())

            return (os.path.basename(documentname),) + ret[1:]

        except IOError as e:
            sys.stderr.write("Could not open testing document %s: %s" %
                    (documentname, e.strerror))
            return (os.path.basename(documentname),'',dict())


    def classify_directory(self, path):
        '''
        Classify a whole directory
        Arguments:
            -path: string containing directory path to classify

        Returns: list of classification tuples
        '''
        returnlist = list()

        try:
            filenames = os.listdir(path)
            # Natural Sort of the filenames
            # Some serious Python Voodoo here
            filenames.sort(key=lambda key: [
                int(x) if x.isdigit() else x.lower()
                for x in re.split('([0-9]+)', key)
                ])
            for filename in filenames:
                filepath = os.path.join(path, filename)

                returnlist.append(self.classify_document(filepath))

        except IOError as e:
            raise IOError("Could not open testing directory (%s): %s" %
                    (path, e.strerror))

        return returnlist

    def word_probability(self, word):
        '''
        Get the probability of a word in each class
        Arguments:
            -word: string

        Returns: a dict or class-probability mappings
        '''
        retvalue = dict()
        for dc in self.doc_class:
            retvalue[dc.name] = dc.word_probability(word)

        return retvalue


    def get_classes(self):
        '''
        Returns a list of document classes in the classifier
        '''
        return list([dc.name for dc in self.doc_class])

    def vocab_size(self):
        '''
        Returns the classifier vocabulary size
        '''
        return len(self.vocab)

    def get_class_doc_count(self, cn):
        for c in self.doc_class:
            if c.name == cn:
                return c.doc_count
