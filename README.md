# english-inflection
Python codes for generating inflected English words (conjugation, plural, comparative/superlative)
There are some works for generating inflected words for English language, but the quality is not very satisfactory.
https://github.com/clips/pattern 
https://github.com/FinNLP/en-inflectors 
The reason of low quality is from either incompleteness of inflection rules or scarce data for ML.
Because inflection is irregular and time-variant thus it is not a good application area of ML(machine learning).
This project explains inflections in detail and then provides codes for inflection.

## Verb conjugation
* Pre-grant prosecution
  * Filing an application - practitioner searches prior arts to clarify the novelty of the invention.
  * Search and examination - examiner searches prior arts to grant or reject the application
  * Appealing to rejection - practitioner searches prior arts to appeal to the rejection
* Post-grant prosecution - a third party searches prior arts to oppose the grant of a patent

There are systems for this prior art search.
They are all based on search engine and database technology.
PATANA project is an NLP application based on up-to-date AI technology for the prior art search.
AI can help human by suggesting search term and/or screening irrelevant patents from the search results.

This project starts with the problem solving of screening irrelevant patents for Korean patents first.
It may be called as patana1ko sub-project of PATANA.
Working with other languages and suggesting search term will be followed.

## Problem description
Search by keyword has been the way of finding prior arts.
Elasticsearch, Solar, Lucene are examples of search engine that can be used for searching by keyword.
The search engines have their own relevence ranking based on a word occurence counting called tf-idf.
This relevence ranking is not very satisfactory for checking whether a patent has similar claims to another one.
Sreening irrelevant patents is done by human after reading considerable portion of patents in search result.
AI will reduce cost for patent drafting, refining, examining by screening irrelevant patents from search results.

## Software requiremants of the patana1ko
* Develop AI-based software that calculated distance between any 2 korean patents
  * Similar patents should be close to each other
  * A patent and its prior art should be close to each other
  * Patents with different topic should not be close to each other
  * Patents with different classifications should not be close to each other

## How to find novelty infringement among huge number of patents
Bag-of-words and modified algorithm are baseline for calculating similarity of sentence and paragraph. 

The paragraph vector disclosed by Le & Mikolov in 2014.
https://cs.stanford.edu/~quocle/paragraph_vector.pdf

The word mover's distance disclosed by Kusner et. al in 2015.
http://proceedings.mlr.press/v37/kusnerb15.pdf

Other recent researches are competing for better performance in both unsupervised and supervised way.
https://medium.com/huggingface/universal-word-sentence-embeddings-ce48ddc8fc3a

The buttom line is that we can get similarity of patents by applying generic technologies.
Patents are relatively well-formed and have nice meta data that can be utilized for accuracy and efficiency.
By utilizing characteristics of patents, we can make these technologies work better for prior art search.
The way how to utilize characteristics of patent will be explained in separate document.

## Process breakdown
* Scrape patents
* Extract texts section by section and extract meta data for each patent
* Split texts sentence by sentence
* Prepare training/validation/test dataset with meta data
* Create AI models for computing distance between any two paragraphs
* Test/Tune AI models and choose the best model for patent comparison
* Creat AI model for computing distance between any two patents
* Test/Tune AI model

## How to use
1. download python files.
2. create sub directories /list, /searched_patents, /searched_patents/html
3. execute search_korean_patents.py with search command and search keywords separated by space
   * patent url list resulted by keyword search will be created as /list/searched_patents.url
4. execute search_korean_patent.py with download command
   * patent html files will be downloaded in /searched_patents/html/
5. execute extract_text.py to extract part of from html
   * with 2 arguments, the directory name where htmls are saved and the part of patent
     * abstract, description, claims, sentences are examples of the part
   * specified part of each patent will be saved in /searched_patents/part/
   * sentences are all texts that is in the form of sentence. (title, drawings, sequence, terms are not sentences)
6. execute concat_text.py to create a big concatanated file
   * with the same 2 arguments
   * concatanation result will be saved as /searched_patents/part.txt
7. execute sbd_text.py for pre-processing
   * with the same 2 arguments
   * SBD(sentence boundary detection) result will be saved as /searched_patents/part_sbd.text
     * SBD can be done by punctuation identification since patents have formality.
   * stop word filtering result will be saved as /searched_patents/part_sbd_words.text
     * stop words may not be static words and they are dependent on the language.
     * Morphological analyzer can be applied to identify postpositional subword for Korean patents.
   * each patent in /searched_patents/part/ will be processed both sentence boundary detection and stop word filtering
8. apply fasttext for word2vec model
   * if run by command-line, fasttext skipgram -input ../searched_patents/sentences_sbd_words.txt  -output sentences
9. execute embed_sentence.py to create sentence vectors for each patent
   * with the same 2 arguments
   * if run by command-line, fasttext print-sentence-vectors sentences.bin < patent_sbd_words.txt > patent_sbd_words.vec
10. execute find_nearest.py with 3 arguments
    * 1st argument is the patent number to find nearest patents
    * 2nd argument is the subdirecory name (searched_patents)
    * 3rd argument is the part name (abstract, description, claims, sentences)
    * then it will calculate distance between the given patent and all other patents in the subdirectory by
      * cosine similarity between averages of sentence vectors of two patents
      * euclidian distence between averages of sentence vectors of two patents

## Caveats
* Components of Korean patents are not unique.
* Korean patents in Google patents are not very consistently prepared.
  * some patents do not have classifications
  * some patents have not sectionized text for the disclosure and enbodiments.
