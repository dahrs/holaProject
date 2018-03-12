#!/usr/bin/python
#-*- coding:utf-8 -*- 

#job Title Extractor using coreference of token ngrams

import re
from nltk.corpus import stopwords


class jobTitleExtractorZack():
    '''
    Implements the job title extractor
    '''
    def __init__( self ):
        pass

    ##############################################################
    to_remove = set(stopwords.words("english") + ['', ' ', '&'])
    pattrn = re.compile(r"[-/,\.\\\s]")
    ##############################################################

    def getNgram_counts(self, pathToSourceFile, to_remove=to_remove, pattrn=pattrn):
        '''
        Makes a dict of every 1-, 2-, 3-gram in the 
        job source file
        '''
        import codecs
        ngram_counts = {}
        openFile = codecs.open(pathToSourceFile, u'r', encoding=u'utf8')
        for index, line in enumerate(openFile):
            tokens = re.split(pattrn, line)
            tokens = list(filter(lambda tok: tok not in to_remove, tokens))
            for n in range(1,4):
                for ngram in self.get_ngrams(n, tokens):
                    ngram_counts[ngram] = ngram_counts.get(ngram, 0)+1
        openFile.close()
        return ngram_counts


    def testZackExtractor(self, sentence):
        '''
        just a test, if we need to call the extractor multiple times we need to
        keep the ngram_counts dict in memory instead of making it over and over
        '''
        ngram_counts = self.getNgram_counts(u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/jobTitles.txt')
        to_remove = set(stopwords.words("english") + ['', ' ', '&'])
        pattrn = re.compile(r"[-/,\.\\\s]")
        return self.get_best(sentence, to_remove, pattrn, ngram_counts)


    #Zack Soliman##############################

    def get_best(self, s, to_remove, pattrn, ngram_counts):
        tokens = re.split(pattrn, s)
        tokens = list(filter(lambda tok: tok not in to_remove, tokens))
        
        if len(tokens) == 0:
            return "<unk>"

        unigram = max(self.get_ngrams(1, tokens), key=lambda x: ngram_counts[x])
        bigram = max(self.get_ngrams(2, tokens), key=lambda x: ngram_counts[x])
        trigram = max(self.get_ngrams(3, tokens), key=lambda x: ngram_counts[x])
        
        if trigram and ngram_counts[trigram] > 100:
            return " ".join(trigram)
        elif bigram and ngram_counts[bigram] > 100:
            return " ".join(bigram)
        else:
            return unigram[0]


    def get_ngrams(self, n, tokens):    
        return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]