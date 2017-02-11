# how to run: python AddCommentsPolarity.py Input/PSG/CommentsDF.csv Results/PSG/polarities.csv Results/PSG/CommentsSentimentAnalysis.csv
import pandas as pd
import sys
import numpy as np
import pdb


# Get Comments filename
comment_filename = sys.argv[1]
# Get polarities filename
polarities_filename = sys.argv[2]
# Get output file
output_file = sys.argv[3]
# Read Comment DataFrame
CommentsDF = pd.read_csv(open(comment_filename, 'rU'), encoding='utf-8', engine='c', sep='|')
# Read Polarities DataFrame
PolarityDF = pd.read_csv(open(polarities_filename, 'rU'), encoding='utf-8', engine='c')
# Add Polarity column to CommentsDF
CommentsWithPolarityDF = pd.concat([CommentsDF, PolarityDF ], axis=1)

# Assign Sentiment according to polarity value
Sentiment_list = [ 'positive' if x > 0 else 'negative' if x < 0 else 'neutre' for x in CommentsWithPolarityDF.CommentPolarity.values]
# Convert list to numpy
Sentiment_list = np.asarray(Sentiment_list)


# Add sentiment column to CommentDF
CommentsWithPolarityDF['Sentiment'] = Sentiment_list
# add comments dataframe
CommentsSentimentDF = CommentsWithPolarityDF[['ID_POST', 'COMMENT_ID', 'MESSAGE', 'Sentiment']]
CommentsSentimentDF.rename(columns={'Sentiment': 'CommentSentiment'}, inplace=True)

# Create DataFrame to aggregate Sentiment per Post
PostSentimentList = []
# Groupby post
for name, group in CommentsWithPolarityDF.groupby(['ID_POST']):
    # Groupby Sentiment and count
    SentimentCount = group.groupby(['Sentiment'])['COMMENT_ID'].count()
    if 'negative' in SentimentCount.keys():
        negative = SentimentCount['negative']
        PostSentimentList.append([name, 'negative', negative])
    else:
        negative = 0
        PostSentimentList.append([name, 'negative', negative])

    if 'positive' in SentimentCount.keys():
        positive = SentimentCount['positive']
        PostSentimentList.append([name, 'positive', positive])
    else:
        positive = 0
        PostSentimentList.append([name, 'positive', positive])

    if 'neutre' in SentimentCount.keys():
        neutre = SentimentCount['neutre']
        PostSentimentList.append([name, 'neutre', neutre])
    else:
        neutre = 0
        PostSentimentList.append([name, 'neutre', neutre])

# convert list to numpy
PostSentimentList = np.reshape(PostSentimentList, (len(PostSentimentList), len(PostSentimentList[0])))
# Create DataFrame Count Sentiment per Post
PostSentimentDF = pd.DataFrame(data=PostSentimentList, columns=['ID_POST', 'Sentiment', 'Count'])
print 'Post sentiment dataframe has number rows {}'.format(PostSentimentDF.shape[0])

pos_neg_neutre_DF = pd.pivot_table(PostSentimentDF, index=['ID_POST'], columns=['Sentiment'], aggfunc=np.sum)
print 'Post beg pos dataframe has number rows {}'.format(pos_neg_neutre_DF.shape[0])
# change columns name
pos_neg_neutre_DF.columns = ['positive', 'negative', 'neutre']
# add id_post as column
pos_neg_neutre_DF['ID_POST'] = pos_neg_neutre_DF.index.values

# merge two data frames
mergeDF = pd.merge(PostSentimentDF, pos_neg_neutre_DF, how='left', on=['ID_POST'])
print "merged data has number rows {}".format(mergeDF.shape[0])

mergeDF.to_csv(output_file, sep=',', index=False)
