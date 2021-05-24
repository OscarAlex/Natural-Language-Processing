# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:23:39 2021

@author: Oscar
"""
import requests
from bs4 import BeautifulSoup
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

#URLs
main_url= 'https://www.grisda.org'
url1= 'https://www.grisda.org/articles?&primary=paleontology&secondary=fossil-kinds-and-sites'
url2= 'https://www.grisda.org/articles?page=2&primary=paleontology&secondary=fossil-kinds-and-sites'
url3= 'https://www.grisda.org/articles?page=2&primary=paleontology&secondary=fossil-kinds-and-sites'

#%%
#Get info from grid boxes
def getInfo(url):
    r= requests.get(url)
    soup= BeautifulSoup(r.text, 'lxml')
    #Get grid with title and link
    grids= soup.section.find('div', {'id': 'article'}).div.div.find_all('div', class_='grid-line')
    
    #Get title, author, date and link
    info= []
    for grid in grids:
        info.append({
            'title_author': grid.h3.text,            
            'date': grid.time.text,
            'link': grid.a['href']
        })
    return info

page1= getInfo(url1)
page2= getInfo(url2)
page3= getInfo(url3)

#%%
#Get title and article 
def getArticle(page_n):
    r= requests.get(main_url+page_n['link'])
    soup = BeautifulSoup(r.text, 'lxml')
    page= soup.find('div', class_='page')
    
    #Return None
    if page == None:
        return None
    
    #Remove figures
    for fig in page.select('figure'):
        fig.extract()
        
    #Get article body
    tex= ''
    for info in page.find_all('p'):
        tex+= info.text
    
    #Split by "footer"
    tex= re.split('ENDNOTES|REFERENCES|References|Footnotes|Supplementary ', tex)[0]
    #Get first bibliography
    bib_init= re.findall(r'(.+doi.+(Summary\. ?|\n)|.+DOI.+(Summary\. ?|\n))', tex)
    #If match, replace
    if bib_init:
        tex= tex.replace(bib_init[0][0], '')
    #Get bibliography
    bib= re.findall(r'\[\d\] [\w&\-, ]+\. [\d]{4}\. .+\[\d\] .+', tex)
    #If match, replace
    if bib:
        tex= tex.replace(bib[0], '')
    #Get cites
    cites= re.findall(r'\[\d+\]|\[\d+[,\-]\d+\]', tex)
    #If match, replace
    if cites:
        for n in cites:
            tex= tex.replace(n, '')
    #Get cites2
    cites2= re.findall(r'\([\w ]+ et al[.|,] [\d]{4}\)', tex)
    #If match, replace
    if cites2:
        for n in cites2:
            tex= tex.replace(n, '')
    #Get Figure mentions
    figs= re.findall(r'\(Fig\. [0-9]+\)|\(Figures? [0-9]+\)', tex)
    if figs:
        for n in figs:
            tex= tex.replace(n, '')
            
    #Get title and article body
    doc= {
        'title': page_n['title_author'],
        'doc': tex
         }
    
    return doc

#Get articles
docs= []
for pagen in [page1, page2, page3]:
    for page in pagen:
        docs.append(getArticle(page))
#Remove None
docs= list(filter(None, docs)) 

#No dinosaurs
del docs[18]
del docs[12]

#Write
"""for doc in docs:
    try:
        txt= open('geo/'+re.sub(r'[^\w\s]','', doc['title'])+'.txt','w+')
        #txt.write(re.sub(r'[^\w\s]','', doc['doc']))
        txt.write(doc['doc'])
        txt.close()
    except:
        continue"""

#%% 
def normalize(tex):
    #Lowercase
    tex= tex.lower()
    #Remove punctuation
    tex= re.sub(r'[^\w\s]','', tex)
    #Remove white spaces
    tex= tex.strip()
    #Stopwords
    stop_words= stopwords.words('english')
    words= ['comment', 'abstract', 'summary', 'introduction']
    stop_words.extend(words)
    
    #Tokenize
    tokens= word_tokenize(tex)
    #Tokens with no stop words
    result= [word for word in tokens if not word in stop_words]
    #Text
    textf= nltk.Text(result)
    
    return textf

#%%
tokens= []
for doc in docs:
    tokens.append(normalize(doc['doc']))
#tokens[:2]

#%% Dispersion plot
for doc, token in zip(docs, tokens):
    #doc.dispersion_plot(['dinosaur', 'fossil', 'god', 'bible'], title='Title')
    nltk.draw.dispersion.dispersion_plot(token, ['dinosaur', 'fossil', 'god', 'bible', 'flood'], title=doc['title'])
    #doc.similar('dinosaur')


#%%
re.findall(r'\([\w ]+ et al[.|,] [\d]{4}\)', docs[17]['doc'])
#re.findall(r'^\[\d+\]|\[\d+[,\-]\d+\]', docs[15]['doc'])#15
#re.findall(r'\[\d+[[,\-]\d+]?\]', docs[15]['doc'])#15
