
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pdb
from textblob import TextBlob
import unicodedata
from translateHack import translate


comment = unicode("une voiture sans intérêt.", "utf-8")
comment = unicodedata.normalize('NFKD', comment).encode('ascii','ignore')
print "unicode comment: {}".format(comment)
# translate
comment = translate(comment, to_language='en', language='fr')
print "translated post: {}".format(comment)
# create textblob
comment = TextBlob(comment)
# check spelling
comment = comment.correct()
print "corrected post: {}".format(comment)


print "polarity: {}".format(comment.sentiment.polarity)
