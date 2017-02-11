# -*- coding: utf-8 -*-
# how to launch: python CommentsSentimentAnalysis.py
import pandas as pd
import numpy as np
from textblob import TextBlob
import unicodedata
from translateHack import translate
import sys
import os
import pdb

# Function applied across DataFrame comments rows
def func(x):
    # Try and cath error when we cannot convert from 'fr' to 'en'
    try:
        # remove french accents
        comment = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
        # Translate using hack
        comment = translate(comment, 'en', 'fr')
        # Create TextBlob object
        comment = TextBlob(comment)
        # Add polarity to list
        polarities.append(comment.sentiment.polarity)
        # just monitoring
        if (len(polarities) % 100 == 0):
            print "... %f comments treated so far " % (len(polarities)/float(DF.shape[0]))
    except:
        polarities.append(0)

# get current directory
path = os.getcwd()
# Read input file
input_file_path = sys.argv[1]
# Read output file
output_file_path = sys.argv[2]

# append path
input_file_path = os.path.join(path, input_file_path)
output_file_path = os.path.join(path, output_file_path)
# Read DataFrame
DF = pd.read_csv(open(input_file_path, 'rU'), sep='|', encoding='utf-8', engine='c', chunksize=10000)
print "end reading file"

for (number, chunk) in enumerate(DF):
    # Initialize polarities list
    polarities = []
    # Apply Sentiment Analysis per row
    chunk.MESSAGE.apply(func)
    # Convert list2DF
    polarities = np.asarray(polarities)
    # create DataFrame
    polaritiesDF = pd.DataFrame(data=polarities, columns=['CommentPolarity'])
    # Store it!!!
    #polaritiesDF.to_csv('Results/polaritiesTail.csv', index=False)
    # append to data
    with open(output_file_path, 'a') as f:
        print "writing chunk %d" %(number)
        # put header if this is the first chunk
        if number==0:
            polaritiesDF.to_csv(f, header=True, index=False)
        else:
            polaritiesDF.to_csv(f, header=False, index=False)

