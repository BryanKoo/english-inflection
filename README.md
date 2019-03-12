# english-inflection
Python codes for obtaining inflected English words (conjugation, plural, comparative/superlative)
Once every inflection is obtained, it can be used to recognize English texts word by word.
For those who want to know what the inflection is, check https://en.wikipedia.org/wiki/Inflection
New inflected word is generated by adding preffix, infix, suffix or chaning vowel to the basic form of the word.

Followings are related to inflection but they are not the concern of this project
* collocating other word to properly complete the inflection (do > have done)
* using other word instead of inflection (must > had to)

## Machine Learning or rule-based ?
There are two notable works for generating inflection for English vocabulary, Pettern.en and en-inflectors.\
https://github.com/clips/pattern https://www.clips.uantwerpen.be/pages/pattern-en \
https://github.com/FinNLP/en-inflectors http://en-inflectors.surge.sh/

Pattern.en is a big project that used machine learning for English NLP, including inflection. 
The accuray of inflection using Pattern.en is said to be above 90%. 
The problem is that we cannot correct each specific error because ML is not deterministic.

en-inflectors is a small project when compared to Pattern.en and rule-based.
The accuracy is not provided but it looks more accurate than Pattern.en.
There are still errors due to incompleteness of inflection rules.
We can correct each specific error with en-inflectors but it is still difficult because inflection rules are combined into complex regular expression.

## Verb conjugation (auxiliary/model verbs as well)
Verbs are inflected to express tense, voice, person, number, etc. and it is called conjugation.
* There are 5 spellings after conjugation
  * infinitive - original form that can be found in English dictionary
  * third person singular(TS) - basic rule is putting 's' (take > takes)
  * present progressive/continuous(PC) - basic rule is putting 'ing' (go > going)
  * past(PA) - basic rule is putting 'ed' (watch > watched)
  * past participle(PP) - basic rule is putting 'ed' (watch > watched)
* Some verbs may have two or more spellings for a specific conjugation that can be used interchangeably.
* Some verbs have two or more different spellings for a specific conjugation according to the meaning.
* Basic rule should be modified a little according to word endings, vowels and consonant phonetics. (go > goes)
* There are many verbs that do not follow the basic or modified rule and those can be called irregular conjugation.
* Auxiliary verbs may not have all 4 spellings (no PP spelling for can, will, ..)

## Noun pluralization (numbers as well)
Nouns are inflected to express number, that is plural.
* There are 2 spellings; singular and plural
  * basic rule is putting 's' (book > books)
* Some nouns are uncountable.
* Some nouns have two or more different spellings for plural that can be used interchangeably.
* Some nouns have two or more different spellings for plural according to the meaning.
* Basic rule should be modified a little according to word endings, vowels and consonant phonetics. (box > boxes)
* There are many nouns that do not follow the basic or modified rule and those can be called irregular pluralization.
* numbers may have plural (fifty > fifties), thus their pluralization should be supported
* pronouns may have plural but mostly is not inflection but another word (I > we), except for other (other > others)

## Adjective/adverb comparison (some determiners as well)
Adjective and adverbs are inflected to express comparison.
* There are 3 spellings after inflection when a word has 1 syllable.
  * positive
  * comparative - basic rule is putting 'er' (fast > faster)
  * superlative - basic rule is putting 'est' (fast > fastest)
* When a word has more than 3 syllables, there are no inflection but use more/most for comparative/superlative.
* Words with 2 syllable are irregular, some use inflection and some use more/most and some use both.
* Some words are uncomparable.
* Some words have two or more different spellings for comparative/superlative that can be used interchangeably.
* Some words have two or more different spellings for comparative/superlative according to the meaning.
* Basic rule should be modified a little according to word endings, vowels and consonant phonetics. (pretty > prettier)
* There are many adjectives/adverbs that do not follow the basic or modified rule and those can be called irregular comparative/superlative.
* Quantifiers, kinds of determiner, may have comparative/superlative (few/fewer/fewest, little/less/least) thus their inflection should be supported

## Software requiremants
* modules: get_conjugation, get_plural, get_comparative
  * prerequisite: irregular inflection list for conjugation, pluralization, comparison
  * input: word, inflection_type(if applicable)
  * check if input word is infinitive/singular/positive or not
  * obtain inflections regarding the input word
  * output: infinitive/singular/positive, inflected word list with inflection type tag

## Process breakdown
* Read irregular inflection list from file
  * tag each word for grammartical usage
* Check whether input word is unconjugatable/uncountable/uncomparable
* Check whether input word is a basic word(infinitive/singular/positive) or not
  * assume given word as a basic word if not solvable (e.g. fell)
  * use infinitive/singular/positive if found instead of the input word
* Check whether the word is in the irregular inflection list
  * get inflections if found
* Apply rule according to word endings, vowels and consonant phonetics.

## Caveats
* Do not check whether the input is proper or not for each inflections.
  * input word may not be English word like 'alskdjf'
  * input word for conjugation may not be verb
  * proper input word should be guranteed by caller of the module
* Syllable counting may not be accurate
  * inflection error due to wrong syllable counting can be handled by adding irregular inflection list
* Doubling last consonant may not be accurate because pronunciation is not considered for the determination.
  * inflection error syllable counting can be handled by adding irregular inflection list
