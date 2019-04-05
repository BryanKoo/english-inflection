#-*- encoding: utf-8 -*-
# 2 syllables are irregular (sometimes both -er and more are used)
# 2 syllables ends with y, ly, lly are most irregular (silly, fully)
# there are none-comparable adjectives and adverbs (wiktionary)
# added functionality of finding positive when input is conparative of superlative
# may not work correctly when positive ends with e > lets provide two possible positives

import json
import re
import pickle
import os, sys
import pdb
reload(sys)
sys.setdefaultencoding('utf-8')

def find_positive_irregular(word):
  for key in irregular_tagged_comps:
    if word == key: return key
    comp_list = irregular_tagged_comps[key]
    for comp in comp_list:
      if word == comp[3:]: return key 
  return ""

# snug, snugger, snuggest
def doubled_consonant(candidate):
  if count_syllable(candidate) == 1 and len(candidate) > 2 and candidate[-1] == candidate[-2]:
    word = candidate[:-1]
    if word[-1] in consonants and word[-1] != 'x' and word[-1] != 'w' and word[-2] in vowels and word[-3] in consonants:
      return True
  return False

def find_positive_regular(word):
  positive = ""
  positives = []
  if word.endswith('iest'):
    positive = word[:-4] + 'y'
  elif word.endswith('ier'):
    positive = word[:-3] + 'y'
  elif word.endswith('est'):
    positive1 = word[:-3]
    positive2 = word[:-2]
    if doubled_consonant(positive1): positive1 = positive1[:-1]
    if doubled_consonant(positive2): positive2 = positive2[:-1]
    positives = [positive1, positive2]
  elif word.endswith('er'):
    positive1 = word[:-2]
    positive2 = word[:-1]
    if doubled_consonant(positive1): positive1 = positive1[:-1]
    if doubled_consonant(positive2): positive2 = positive2[:-1]
    positives = [positive1, positive2]
  else:
    return ""

  if positive != "":
    comp_list = get_regular_comp(positive)
    for comp in comp_list:
      if word == comp[3:]: return positive
  elif len(positives) > 0:
    for positive in positives:
      comp_list = get_regular_comp(positive)
      for comp in comp_list:
        if word == comp[3:]: return positive
  return ""

def tag_comps(infinitive, comps):
  tagged_comps = []
  untagged_comps = []
  for comp in comps:
    if comp.endswith('er'):
      tagged_comps.append('CO:'+comp)
    elif comp.endswith('est'):
      tagged_comps.append('SU:'+comp)
    else:
      untagged_comps.append(comp)
  if len(untagged_comps) == 1:
    tagged_comps.append('SU:'+untagged_comps[0])
  elif len(untagged_comps) == 2:
    tagged_comps.append('CO:'+untagged_comps[0])
    tagged_comps.append('SU:'+untagged_comps[1])
  elif len(untagged_comps) > 0:
    pdb.set_trace()
  return tagged_comps

def append_comp(infinitive, comp):
  tagged_comps = tag_comps(infinitive, comp)
  if infinitive in irregular_tagged_comps:
    for word in tagged_comps:
      if word not in irregular_tagged_comps[infinitive]:
        irregular_tagged_comps[infinitive].append(word)
  else:
    irregular_tagged_comps[infinitive] = tagged_comps

# wrong counting but good for comparative: quiet, easy
# wrong counting: fine
def count_syllable(word):
  num_syll = 0
  is_vowel = False
  was_vowel = False
  for ch in word:
    if ch in vowels or ch == 'y':
      is_vowel = True
    else:
      is_vowel = False
    if is_vowel and was_vowel == False:
      num_syll += 1
    was_vowel = is_vowel
  if word[-1] == 'e' and word[-2] in consonants:
    num_syll -= 1
  return num_syll

# word /t comparative superlative
def read_comps(ufile):
  uf = open(ufile, 'r')
  while True:
    line = uf.readline().strip()
    if not line: break
    comp = []
    line = line.replace(" or ", " ")
    line = line.replace(", ", " ")
    tokens = line.split('\t')
    infinitive = tokens[0].strip()
    if len(tokens) > 1:
      remained = tokens[1].strip()
      tokens = remained.split(' ')
      for token in tokens:
        if token in comp:
          pdb.set_trace()
        else:
          comp.append(token.strip())
    append_comp(infinitive, comp)
  uf.close()

def get_irregular_comp(word):
  if word in irregular_tagged_comps:
    return irregular_tagged_comps[word]
  else:
    return None

def regular_short_comp(word):
  if word.endswith('e'):
    return ['CO:'+word+'r', 'SU:'+word+'st']
  else:
    return ['CO:'+word+'er', 'SU:'+word+'est']

# bloodier, sillier, chillier, more fully, holier, more briefly, uglier
# ly is irregular: holier should be defined as irregular
# length may be used for regulation
def ends_y(word):
  if word[-1] == 'y':
    if word.endswith('illy'):
      return ['CO:'+word[:-1]+'ier', 'SU:'+word[:-1]+'iest']
    elif word.endswith('ly'):
      if len(word) <= 4:
        return ['CO:'+word[:-1]+'ier', 'SU:'+word[:-1]+'iest']
      else:
        return []
    elif word[-2] in consonants:
      return ['CO:'+word[:-1]+'ier', 'SU:'+word[:-1]+'iest']
    else:
      return ['CO:'+word+'er', 'SU:'+word+'est']
  else:
    return None

def ends_single_consonants(word):
  if word[-1] in consonants:
    if len(word) < 3: return None # up, in are irregular
    if word.endswith('w') or word.endswith('x'):
      return ['CO:'+word+'er', 'SU:'+word+'est']
    elif word[-2] in vowels and word[-3] not in vowels: # double the last consonant
      return ['CO:'+word+word[-1]+'er', 'SU:'+word+word[-1]+'est']
    else:
      return ['CO:'+word+'er', 'SU:'+word+'est']
  else:
    return None

def get_regular_comp(word):
  comp = ends_y(word)
  if comp == None and count_syllable(word) < 2:
    comp = ends_single_consonants(word)
    if comp == None: comp = regular_short_comp(word)
  if comp == None: comp = []
  return comp

def get_comparative(word):
  if word in poly_comps:
    positive = word
  else:
    positive = find_positive_irregular(word)
    if positive == "":
      positive = find_positive_regular(word)
      if positive == "":
        positive = word

  comp = get_irregular_comp(positive)
  if comp == None:
    num_syll = count_syllable(positive)
    #print "not in irregular list, number of syllble is", num_syll
    if num_syll > 2:
      comp = []
    else:
      if positive.endswith('ous') or positive.endswith('ful') or positive.endswith('ed') or positive.endswith('ing') \
        or positive.endswith('est') or positive.endswith('less') or positive.endswith('able') or positive.endswith('ant') \
        or positive.endswith('ive') or positive.endswith('ent') or positive.endswith('free'):
        comp = []
      else:
        comp = get_regular_comp(positive)
  return positive, comp

irregular_tagged_comps = {}
vowels = ['a','e', 'i', 'o', 'u']
consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'q', 'p', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z']
poly_comps = ['eager', 'bitter', 'silver', 'tender', 'slender', 'sheer', 'sober', 'clever', 'proper']

path = os.path.split(__file__)[0]
read_comps(os.path.join(path, "cefr_comparatives.tsv"))
read_comps(os.path.join(path, "irregular_comparatives.txt"))
read_comps(os.path.join(path, "uncomparables.txt"))

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "need an adjective or adverb to get comparative/superlative"
    sys.exit()
  word = sys.argv[1]

  positive, comp = get_comparative(word)
  print positive, comp
