#-*- encoding: utf-8 -*-
# generate all conjugation of a verb/auxiliary_verb/modal_verb
# must >> 'had to' is no conjugation
# added consonant doubling - jam
# unconjugatable word should be covered by irregular (must, ought)
# added functionality of finding infinitive when conjugated word in given
# check for the case when conjugated spell is the same as infinitive: fell/fall, found/find, lay/lie
# added show tenses with each conjugation (TS:third singular, PC:present continous, PA:past, PP:past participle)
import json
import re
import pickle
import os, sys
import pdb
from get_comparative import count_syllable
reload(sys)
sys.setdefaultencoding('utf-8')

def find_infinitive_irregular(word):
  for key in irregular_tagged_conjus:
    if word == key: return key
    conju_list = irregular_tagged_conjus[key]
    for conju in conju_list:
      if word == conju[3:]: return key
  return ""

def doubled_consonant(candidate):
  if count_syllable(candidate) == 1 and len(candidate) > 3 and candidate[-1] == candidate[-2]:
    word = candidate[:-1]
    if word[-1] in consonants and word[-1] != 'x' and word[-1] != 'w' and word[-2] in vowels and word[-3] in consonants:
      return True
  return False

# -ying should be covered by irregular conjugation
# -es, -ies, -ied should be covered by regular conjugation (kisses, fries, fried)
def find_infinitive_regular(word):
  if word.endswith('ing'):
    infinitive = word[:-3]
    if doubled_consonant(infinitive): infinitive = infinitive[:-1]
  elif word.endswith('ied'):
    infinitive = word[:-3] + 'y'
  elif word.endswith('ed'):
    infinitive = word[:-2]
    if doubled_consonant(infinitive): infinitive = infinitive[:-1]
  elif word.endswith('ies'):
    infinitive = word[:-3] + 'y'
  elif word.endswith('es'):
    infinitive = word[:-2]
  elif word.endswith('s'):
    infinitive = word[:-1]
  else:
    return ""
  conju_list = get_regular_conju(infinitive)
  for conju in conju_list:
    if word == conju[3:]: return infinitive
  return ""

def tag_conjus(infinitive, conjus):
  tagged_conjus = []
  untagged_conjus = []
  for conju in conjus:
    if conju.endswith('s'):
      tagged_conjus.append('TS:'+conju)
    elif conju.endswith('ing'):
      tagged_conjus.append('PC:'+conju)
    else:
      untagged_conjus.append(conju)
  if len(untagged_conjus) == 2:
    if untagged_conjus[0] == untagged_conjus[1]:
      tagged_conjus.append('PA:'+untagged_conjus[0])
      tagged_conjus.append('PP:'+untagged_conjus[1])
    elif untagged_conjus[0][-2:] != 'ed' and untagged_conjus[1][-2:] != 'ed':
      tagged_conjus.append('PA:'+untagged_conjus[0])
      tagged_conjus.append('PP:'+untagged_conjus[1])
    else: # when 2 past and 2 pp are the same (which word?)
      tagged_conjus.append('PA:'+untagged_conjus[0])
      tagged_conjus.append('PP:'+untagged_conjus[1])
  elif len(untagged_conjus) == 1:
    tagged_conjus.append('PA:'+untagged_conjus[0])
  elif len(untagged_conjus) == 4:
    tagged_conjus.append('PA:'+untagged_conjus[0])
    tagged_conjus.append('PA:'+untagged_conjus[1])
    tagged_conjus.append('PP:'+untagged_conjus[2])
    tagged_conjus.append('PP:'+untagged_conjus[3])
  elif len(untagged_conjus) == 6:
    tagged_conjus.append('PA:'+untagged_conjus[0])
    tagged_conjus.append('PA:'+untagged_conjus[1])
    tagged_conjus.append('PA:'+untagged_conjus[2])
    tagged_conjus.append('PP:'+untagged_conjus[3])
    tagged_conjus.append('PP:'+untagged_conjus[4])
    tagged_conjus.append('PP:'+untagged_conjus[5])
  elif len(untagged_conjus) == 3:
    if infinitive in ['hew', 'mow', 'rive', 'shave', 'shear', 'smite', 'swell', 'tread', 'melt'] \
      or (len(infinitive) >= 3 and infinitive[-3:] in ['get', 'sew', 'sow', 'saw']) \
      or (len(infinitive) >= 4 and infinitive[-4:] in ['bear', 'beat', 'show', 'lade']) \
      or (len(infinitive) >= 5 and infinitive[-5:] in ['strew', 'prove', 'slide']):
      tagged_conjus.append('PA:'+untagged_conjus[0])
      tagged_conjus.append('PP:'+untagged_conjus[1])
      tagged_conjus.append('PP:'+untagged_conjus[2])
    elif infinitive in ['abide', 'bid', 'dive', 'shrink', 'shrive', 'stink', 'strike', 'dare', 'spin', 'stride'] \
      or (len(infinitive) >= 3 and infinitive[-3:] in ['bid']) \
      or (len(infinitive) >= 4 and infinitive[-4:] in ['sink']) \
      or (len(infinitive) >= 6 and infinitive[-6:] in ['spring']):
      tagged_conjus.append('PA:'+untagged_conjus[0])
      tagged_conjus.append('PA:'+untagged_conjus[1])
      tagged_conjus.append('PP:'+untagged_conjus[2])
    else:
      pdb.set_trace()
  elif len(untagged_conjus) == 0:
    pass
  elif len(untagged_conjus) == 5:
    if infinitive in ['abide']:
      tagged_conjus.append('PA:'+untagged_conjus[0])
      tagged_conjus.append('PA:'+untagged_conjus[1])
      tagged_conjus.append('PP:'+untagged_conjus[2])
      tagged_conjus.append('PP:'+untagged_conjus[3])
      tagged_conjus.append('PP:'+untagged_conjus[4])
    else:
      pdb.set_trace()
  else:
    pdb.set_trace()
  return tagged_conjus
      
# append given irregular conjugation to infinitive
# internally append regular conjugations
def append_conjus(infinitive, conju):
  if infinitive in irregular_tagged_conjus:  # aleady appended but may have more conjugation
    tagged_conjus = tag_conjus(infinitive, conju)
    for word in tagged_conjus:
      if word not in irregular_tagged_conjus[infinitive]:
        irregular_tagged_conjus[infinitive].append(word)
  else:
    has_ing = False
    has_s = False
    if infinitive in auxiliary or infinitive in modal:
      has_ing = True
      has_s = True
    for word in conju:
      if word.endswith('s'):
        has_s = True
      if word.endswith('ing'):
        has_ing = True
    if not has_s:
      if infinitive[-1] == 'y':
        if infinitive[-2] in consonants:
          conju.append(infinitive[:-1]+'ies')
        else:
          conju.append(infinitive+'s')
      elif infinitive.endswith('ch') or infinitive.endswith('sh') or infinitive[-1] == 'x' or infinitive[-1] == 's' or infinitive[-1] == 'z' or infinitive.endswith('o'):
        conju.append(infinitive+'es')
      else:
        conju.append(infinitive+'s')
    if not has_ing:
      if infinitive[-1] == 'e':
        if infinitive[-2] == 'i':
          conju.append(infinitive[:-2]+'ying')
        else:
          conju.append(infinitive[:-1]+'ing')
      else:
        conju.append(infinitive+'ing')
    irregular_tagged_conjus[infinitive] = tag_conjus(infinitive, conju)

def read_cefr_conjus(ufile):
  uf = open(ufile, 'r')
  while True:
    conju = []
    line = uf.readline().strip()
    if not line: break
    tokens = line.split('\t')
    infinitive = tokens[0].strip()
    remained = tokens[1].strip()
    tokens = remained.split(',')
    if len(tokens) == 1:
      if tokens[0].count("-") == 2:
        if tokens[0].count("ll") == 1:  # -ling is used as well as -lling
          conju.append(infinitive + "ing")
        conju.append(infinitive + infinitive[-1] + "ing")
        if tokens[0].count("ll") == 1:  # -led is used as well as -lled
          conju.append(infinitive + "ed")
        conju.append(infinitive + infinitive[-1] + "ed")
        conju.append(infinitive + "s")
      elif tokens[0].count("-") == 4:   # both doubling and non-doubling are used
        conju.append(infinitive + "ing")
        conju.append(infinitive + infinitive[-1] + "ing")
        conju.append(infinitive + "ed")
        conju.append(infinitive + infinitive[-1] + "ed")
        conju.append(infinitive + "s")
      elif tokens[0].strip() != "":
        conju.append(tokens[0])
    else:
      remained = remained.replace(" or ", ", ")
      tokens = remained.split(',')
      for token in tokens:
        if token.strip() != "":
          conju.append(token.strip())
    append_conjus(infinitive, conju)
  uf.close()

def read_epage_conjus(ufile):
  uf = open(ufile, 'r')
  while True:
    conju = []
    line = uf.readline().strip()
    if not line: break
    if len(line) == 1: continue
    line = re.sub(r'\(.*\)', '', line)
    line = line.replace(" / ", "\t")
    line = line.replace(",", "\t")
    line = line.replace("  ", "\t")
    line = line.replace("[?]", "")
    line = line.replace("[", "")
    line = line.replace("]", "")
    line = line.replace("REGULAR", "")
    tokens = line.split('\t')
    infinitive = tokens[0].strip()
    for i in range(1, len(tokens)):
      if tokens[i].count("-ll-") > 0:
        conju.append(infinitive + "ing")
        conju.append(infinitive + infinitive[-1] + "ing")
        conju.append(infinitive + "ed")
        conju.append(infinitive + infinitive[-1] + "ed")
        conju.append(infinitive + "s")
      elif tokens[i].strip() != "":
        conju.append(tokens[i].strip())
    append_conjus(infinitive, conju)
  uf.close()

def read_ginger_conjus(ufile):
  uf = open(ufile, 'r')
  while True:
    conju = []
    line = uf.readline().strip()
    if not line: break
    if len(line) == 1: continue
    line = re.sub(r'\(.*\)', '', line)
    line = line.replace("/", "\t")
    line = line.replace("  ", "\t")
    tokens = line.split('\t')
    infinitive = tokens[0].strip()
    for i in range(1, len(tokens)):
      if tokens[i].strip() != "":
        conju.append(tokens[i].strip())
    append_conjus(infinitive, conju)
  uf.close()

def read_usinge_conjus(ufile):
  uf = open(ufile, 'r')
  while True:
    conju = []
    line = uf.readline().strip()
    if not line: break
    if len(line) == 1: continue
    line = line.replace("/", " ")
    tokens = line.split(' ')
    infinitive = tokens[0].lower().strip()
    for i in range(1, len(tokens)):
      if tokens[i].strip() != "":
        conju.append(tokens[i].lower().strip())
    append_conjus(infinitive, conju)
  uf.close()

def get_irregular_conju(word):
  if word in irregular_tagged_conjus:
    return irregular_tagged_conjus[word]
  else:
    return None

def most_regular(word):
  return ['TS:'+word+'s', 'PC:'+word+'ing', 'PA:'+word+'ed', 'PP:'+word+'ed']

# rule for doubling consonant
# two or more syllables should treated as irregular conjugation
def regular_one_syllable(word):
  if count_syllable(word) == 1 and len(word) > 2:
    if word[-1] in consonants and word[-1] != 'x' and word[-1] != 'w' and word[-2] in vowels and word[-3] in consonants:
      return ['TS:'+word+'s', 'PC:'+word+word[-1]+'ing', 'PA:'+word+word[-1]+'ed', 'PP:'+word+word[-1]+'ed']
  return None

def regular_endswith_e(word):
  if word[-1] == 'e':
    if word[-2] in ['e', 'y', 'o']: # free, dye, tiptoe
      return ['TS:'+word+'s', 'PC:'+word+'ing', 'PA:'+word+'d', 'PP:'+word+'d']
    elif word[-2] == 'i': # die, tie
      return ['TS:'+word+'s', 'PC:'+word[:-2]+'ying', 'PA:'+word+'d', 'PP:'+word+'d']
    else: # sue, love
      return ['TS:'+word+'s', 'PC:'+word[:-1]+'ing', 'PA:'+word+'d', 'PP:'+word+'d']
  else:
    return None

def regular_endswith_y(word):
  if word[-1] == 'y':
    if word[-2] in consonants:  # study, fly, carry, cry, worry, reply
      return ['TS:'+word[:-1]+'ies', 'PC:'+word+'ing', 'PA:'+word[:-1]+'ied', 'PP:'+word[:-1]+'ied']
    else: # enjoy, play, stay
      return most_regular(word)
  else:
    return None

# put es instead of s for 3rd person singular for a verb ends with s(ss), sh, ch, x, z, o
# kiss, buzz, box, polish, preach, solo
def regular_third_singular_es(word):
  if word.endswith('ch') or word.endswith('sh') or word[-1] == 'x' or word[-1] == 's' or word[-1] == 'z' or word[-1] == 'o':
    return ['TS:'+word+'es', 'PC:'+word+'ing', 'PA:'+word+'ed', 'PP:'+word+'ed']
  else:
    return None

# Verbs with more than one syllable ending in l double the final letter before suffixing in Britain English
# cancel > cancelled (US canceled)
# handled as irregular conjugation
def ends_l(word):
  pass

def regular_endswith_c(word):
  if word.endswith('c'): # panic, mimic, traffic, picnic
    return ['TS:'+word+'s', 'PC:'+word+'king', 'PA:'+word+'ked', 'PP:'+word+'ked']
  else:
    return None

def get_regular_conju(word):
  conju = regular_endswith_e(word)
  if conju == None: conju = regular_endswith_y(word)
  if conju == None: conju = regular_third_singular_es(word)
  if conju == None: conju = regular_endswith_c(word)
  if conju == None: conju = regular_one_syllable(word)
  if conju == None: conju = most_regular(word)
  return conju

def get_conjugation(word):
  if word in poly_conjus or word in irregular_tagged_conjus:
    infinitive = word
  else:
    infinitive = find_infinitive_irregular(word)
    if infinitive == "":
      if word.endswith('s'):
        infinitive = word
      else:
        infinitive = find_infinitive_regular(word)
      if infinitive == "":
        infinitive = word
  conju = get_irregular_conju(infinitive)
  if conju == None: conju = get_regular_conju(infinitive)
  return infinitive, conju

irregular_conjus = {}
irregular_tagged_conjus = {}
vowels = ['a','e', 'i', 'o', 'u']
consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'q', 'p', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z']
auxiliary = ['be', 'do', 'have']
modal = ['can', 'may', 'must', 'ought', 'shall', 'will']
poly_conjus = ['found', 'fell', 'lay', 'bind', 'saw', 'ground', 'wound', 'rent', 'resent']

path = os.path.split(__file__)[0]
read_cefr_conjus(os.path.join(path, "cefr_conjugations.tsv"))
read_epage_conjus(os.path.join(path, "englishpage_conjugations.txt"))
read_ginger_conjus(os.path.join(path, "ginger_conjugations.txt"))
read_usinge_conjus(os.path.join(path, "usingenglish_conjugations.txt"))

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "need a verb to get conjugation"
    sys.exit()
  word = sys.argv[1]
  infinitive, conju = get_conjugation(word)
  print infinitive, conju
