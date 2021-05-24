# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 17:42:55 2021

@author: Oscar
"""
import requests
from bs4 import BeautifulSoup
import re
from nltk.tokenize import word_tokenize
#from nltk.corpus import stopwords
import nltk
from nltk.probability import FreqDist

#URLs
main_url= 'https://www.grisda.org'
url1= 'https://www.grisda.org/articles?primary=geology&secondary=geologic-processes'
url2= 'https://www.grisda.org/articles?page=2&secondary=geologic-processes'
url3= 'https://www.grisda.org/articles?page=3&secondary=geologic-processes'
url4= 'https://www.grisda.org/articles?page=4&secondary=geologic-processes'

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

#Get grid boxes
page1= getInfo(url1)
page2= getInfo(url2)
page3= getInfo(url3)
page4= getInfo(url4)

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
    tex= re.split('ENDNOTES|Endnotes|REFERENCES|References|Footnotes|FOR FURTHER STUDY|LITERATURE CITED', tex)[0]
    #Get first bibliography
    bib_pat= r'(.+doi.+(Summary\. ?|\n)|.+DOI.+(Summary\. ?|\n))'
    tex= re.sub(bib_pat,'', tex)
    #bib_init= re.findall(r'(.+doi.+(Summary\. ?|\n)|.+DOI.+(Summary\. ?|\n))', tex)
    #If match, replace
    #if bib_init:
     #   tex= tex.replace(bib_init[0][0], '')
    
    #Get bibliography
    #bib= re.findall(r'\[\d\] [\w&\-, ]+\. [\d]{4}\. .+\[\d\] .+', tex)
    #If match, replace
    #if bib:
     #   tex= tex.replace(bib[0], '')
        
    #Get cites
    cites_pat= r'\[[\w\.;,\- ]+\]'
    tex= re.sub(cites_pat,'', tex)
    #cites= re.findall(r'\[[\w\.;,\- ]+\]', tex)
    #If match, replace
    #if cites:
     #   for n in cites:
      #      tex= tex.replace(n, '')
    
    #Get parenthesis
    pars_pat= r'\([\w\.;,\- ]+\)'
    tex= re.sub(pars_pat,'', tex)
    #pars= re.findall(r'\([\w\.;,\- ]+\)', tex)
    #If match, replace
    #if pars:
     #   for n in pars:
      #      tex= tex.replace(n, '')
    
    #Get Figure mentions
    figs_pat= r'[F|f]ig[\.\w]+ [\w,\- ]+|see [F|f]ig[\.\w]+ [\w,\- ]+'
    tex= re.sub(figs_pat,'', tex)
    #figs= re.findall(r'[F|f]ig[\.\w]+ [\w,\- ]+|see [F|f]ig[\.\w]+ [\w,\- ]+', tex)
    #if figs:
     #   for n in figs:
      #      tex= tex.replace(n, '')
    
    #Get e.g.s mentions
    #egs= re.findall(r'\(e\.g\.[\w, ]+\)', tex)
    #if egs:
     #   for n in egs:
      #      tex= tex.replace(n, '')
    
    #Get stop words
    strwords= r'WHAT THIS ARTICLE IS ABOUT|ABSTRACT|INTRODUCTION|ACKNOWLEDGMENTS?|CONCLUSIONS?|Conclusions?|SUMMARY|DISCUSSION|Geoscience Research Institute'
    tex= re.sub(strwords,'', tex)
    #swords= re.findall(strwords, tex)
    #If match, replace
    #if swords:
     #   for n in swords:
      #      tex= tex.replace(n, '')
            
    #Get title and article body
    doc= {
        'title': page_n['title_author'],
        'doc': tex
         }
    
    return doc

#Get articles
docs= []
for pagen in [page1, page2, page3, page4]:
    for page in pagen:
        docs.append(getArticle(page))
#Remove None
docs= list(filter(None, docs)) 
#Remove biblio
docs[8]['doc']= re.split('Ariel A. Roth', docs[8]['doc'])[0]

#Remove film review
del docs[4]


#%%
"""for doc in docs:
    try:
        txt= open('C:/Users/Oscar/Documents/Python Scripts/nltk/geo/'+re.sub(r'[^\w\s]','', doc['title'])+'.txt','w+')
        txt.write(re.sub(r'[^\w\s\.]','', doc['doc']))
        #doc['doc']= doc['doc'].encode('utf8')
        #txt.write(doc['doc'])
        txt.close()
    except:
        continue"""
#re.sub(r'[^\w\s\.,;]','', docs[0]['doc'])
#docs[0]['doc'].encode('utf8')
#%%

def normalize(tex):
    #Lowercase
    tex= tex.lower()
    #Remove punctuation
    tex= re.sub(r'[^\w\s]','', tex)
    #Remove white spaces
    tex= tex.strip()
    #Stopwords
    #stop_words= stopwords.words('english')
    #words= ['comment', 'abstract', 'summary', 'introduction']
    #stop_words.extend(words)
    
    #Tokenize
    tokens= word_tokenize(tex)
    #Tokens with no stop words
    #result= [word for word in tokens if not word in stop_words]
    #Text
    #textf= nltk.Text(result)
    textf= nltk.Text(tokens)
    
    return textf

tokens= []
for doc in docs:
    tokens.append(normalize(doc['doc']))

#Lemmatizer
wnl= nltk.WordNetLemmatizer()
tokens_lems= []
all_lems= []
for tt in tokens:
    lems= []
    for t in tt:
        lems.append(wnl.lemmatize(t))
        all_lems.append(wnl.lemmatize(t))
    tokens_lems.append(nltk.Text(lems))
    #[wnl.lemmatize(t) for t in tokens]

all_lems_tokens= nltk.Text(all_lems)

#%% Dispersion plot
#De las palabras, la que más se utiliza es flood, aunque el artículo tenga poco que ver con el tema
for doc, token in zip(docs, tokens_lems):
    nltk.draw.dispersion.dispersion_plot(token, ['flood', 'fossil', 'layer', 'pliocene', 'miocene', 'erosion'], title=doc['title'])

#for doc, token in zip(docs, tokens_lems):
 #   nltk.draw.dispersion.dispersion_plot(token, ['flood', 'fossil', 'layer', 'tectonic', 'age', 'erosion'], title=doc['title'])

#%% Context flood

for doc, token in zip(docs, tokens):
    print(doc['title'])
    token.common_contexts(['flood', 'fossil'])
    print()

all_lems_tokens.common_contexts(['flood', 'fossil'])

#%% Concordance flood

for doc, token in zip(docs, tokens):
    print(doc['title'])
    token.concordance('flood')
    print()

#%% Similar

for doc, token in zip(docs, tokens):
    print(doc['title'])
    token.similar('flood')
    print()

#%%
#tokens_list= [item for sublist in t for item in sublist]

fdist= FreqDist([w for w in all_lems if len(w) > 5]).most_common(30)
fdist

[w for w in all_lems if len(w) > 4]

#%%

#re.findall(r'\[[\w\.;,\- ]+\]', '[123 et. al ds]')
#re.findall(r'\([F|f]ig[\.\w]+ [\w,\- ]+\)|\(see [F|f]ig[\.\w]+ [\w,\- ]+\)', '(fig. A-B)')
#re.findall(r'WHAT THIS ARTICLE IS ABOUT|ACKNOWLEDGMENTS?|CONCLUSIONS?|INTRODUCTION|Geoscience Research Institute|SUMMARY|DISCUSSION', ' are likely sources for these organic remains. CONCLUSION Examination of the contact between the Miocene Columbia River Basalt and the Pleistocene Palouse loess revealed no gully erosion except for Missoula Flood and modern erosion, both of which were excluded from the study. A thin layer of what appears to be a weathering profile mantles the top of the last basalt flow. Pre-Missoula Flood erosion consisted of a minor amount of smooth, broad sheet erosion, the cause of which has yet to be determined. A lapse of 14 million years between the last lava flow and the deposition of the loess is not supported by the data from this research. ACKNOWLEDGMENT I wish to thank the Geoscience Research Institute for their encouragement')
