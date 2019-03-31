#-*- encoding: utf-8 -*-
# check inflection with pattern.en
# make questions from the database with starting from the input level
# schema word_bymeanings : mid(pk), frequency(index), word(not null), pos(not null), meaning(not null), synopsis, examples
# schema us_bymeanings : uid(pk), mid(fk), us_word(not null)

import sqlite3
import re
import os, sys
import pdb
import random
from pattern.en import conjugate, pluralize, lexeme, comparative, superlative
from parse_cefr import is_sentence
reload(sys)
sys.setdefaultencoding('utf-8')

def get_1pos(pos):
  tokens = pos.split(";")
  if len(tokens) == 1:
    return pos + "%"
  else:
    return tokens[1].strip() + "%"

def remove_punctuation(word):
  removed = ""
  for ch in word:
    if ch not in ['"', "'", ',', '?', '!', '.', '-', ':']:
      removed += ch
    elif removed != "":
      break
  return removed

def remove_front_paren(meaning):
  if meaning.startswith("("):
    meaning = re.sub(r'\(.*\)', '', meaning)
  return meaning.strip()

def create_connection(db_file):
  try:
    conn = sqlite3.connect(db_file)
    return conn
  except sqlite3.Error as e:
    print(e)
    pdb.set_trace()
  return None

def select_questions(conn):
  sql = "select word, pos, examples from words_bymeaning;"
  try:
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
  except sqlite3.Error as e:
    print(e)

  return rows

def has_word(word, example):
  if word.count(" ") > 0:
    pos = example.lower().find(word.lower())
    if pos >= 0 and example[pos+len(word)] in [' ', '.', '?', '!', '"', "'", ',', ':', ';']:
      return True
    pos = remove_punctuation(example).lower().find(word.lower())
    if pos >= 0 and example[pos+len(word)] in [' ', '.', '?', '!', '"', "'", ',', ':', ';']:
      return True
  else:
    tokens = example.split(" ")
    for token in tokens:
      if remove_punctuation(word).lower() == remove_punctuation(token).lower():
        return True
  return False

def find_inflected(word, pos, line):
  conjus = ['inf', '1sg', '2sg', '3sg', 'pl', 'part', 'p', '1sgp', '2sgp', '3sgp', 'ppl', 'ppart']
  if pos.startswith("NOUN") or pos.startswith("DETERMINER") or pos.startswith("NUMBER") or pos.startswith('PRONOUN'):
    plural = pluralize(word)
    if has_word(plural, line): return plural
  elif pos.startswith("VERB") or pos.startswith("AUXILIARY VERB") or pos.startswith("MODAL VERB"):
    conjugateds = lexeme(word)
    for conjugated in conjugateds:
      if has_word(conjugated, line): return conjugated
    print lexeme(word)
  elif pos.startswith("ADJECTIVE") or pos.startswith("ADV"):
    comp = comparative(word)
    sup = superlative(word)
    if has_word(comp, line): return comp
    if has_word(sup, line): return sup
  print "cannot find inflected", word, pos, line
  return ""

def find_example(word, pos, lines):
  inflection = ""
  found = ""
  example = ""
  for line in lines:
    if has_word(word, line):
      found = word
      example = line
      break
    else:
      found = find_inflected(word, pos, line)
      if found != "":
        example = line
        break
  return found, example

def make_qna3(conn):
  qrows = select_questions(conn)
  qnum = 0
  for qrow in qrows:
    word = qrow[0]
    pos = get_1pos(qrow[1])
    examples = qrow[2]
    lines = examples.split('\n')
    word, example = find_example(word, pos, lines)
    print qnum, word
    qnum += 1

if __name__ == "__main__":
  dbfile = "../cefr/cefr.db"
  conn = create_connection(dbfile)
  make_qna3(conn)
  conn.close()
