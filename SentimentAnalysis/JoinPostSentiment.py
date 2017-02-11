import pandas as pd
import pdb
import sys
import os
sentiment_analysis_filename = sys.argv[1]
posts_filename = sys.argv[2]
output_filename = sys.argv[3]
# get current path
path = os.getcwd()

# Read Sentiment Analysis DataFrame
SentimentDF = pd.read_csv(os.path.join(path, sentiment_analysis_filename), sep=',')

# Read Posts DataFrame
PostDF = pd.read_csv(open(os.path.join(path, posts_filename), 'rU'), encoding='utf-8', engine='c', sep=',', dtype={'ID_PAGE': 'str'})
# Add sentiments for posts that have been evaluated (left join)
mergeDF = pd.merge(PostDF, SentimentDF, how='left', on=['ID_POST'])
# Save DataFrame to csv File
mergeDF.to_csv(os.path.join(path, output_filename), index=False)
