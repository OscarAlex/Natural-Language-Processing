# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 17:52:43 2021

@author: Oscar
"""
import nltk

#nltk.download('gutenberg')
#nltk.download('genesis')
#nltk.download('inaugural')
#nltk.download('nps_chat')
#nltk.download('webtext')
#nltk.download('treebank')

#%%
from nltk.book import *
#Concordancia
text1.concordance('monstrous')
#Palabras más cercanas
text1.similar('monstrous')
#Partes de un texto donde están estas palabras
text4.dispersion_plot(["citizens", "democracy", "freedom", "duties", "America"])
