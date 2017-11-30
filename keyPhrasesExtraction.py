# An implementation of RAKE algorithm for Chinese test based on python 3.
# The algorithm is described in:
# Rose, S., D. Engel, N. Cramer, and W. Cowley (2010).
# Automatic keyword extraction from indi-vidual documents.
# In M. W. Berry and J. Kogan (Eds.), Text Mining: Applications and Theory.unknown: John Wiley and Sons, Ltd.

import re
import operator
from math import log
# for Chinese word segmentation
import jieba

debug = False
test = True

def load_text(text_file_path):
	'''
	Utility function to load Chinese text from a file
	:param text_file_path: path of a file containing Chinese text
	:return: the Chinese text
	'''
	text = open(text_file_path, encoding = 'utf8').read()
	return text

def load_stop_words(stop_word_file_path):
	'''
	Utility function to load stop words from a file and return as a list of words
	:param stop_word_file_path: path of a file containing Chinese stop words
	:return: a list of Chinese stop words
	'''
	stop_words = []
	for stp_wd in open(stop_word_file_path, encoding = 'utf8'):
		stop_words.append(stp_wd.strip())
	return stop_words

def separate_words(text, min_word_return_size):
	'''
	Utility function to return a list of all words that are have a length greater than a specified number of characters
	:param text: the text that must be split in to words
	:param min_word_return_size: The minimum length of the Chinese word(s) must have to be included
	:return: a list of separate words
	'''
	words = []
	for wd in jieba.cut(text, cut_all = False):
		if len(wd) > min_word_return_size and wd != '':
			words.append(wd)
	return words

def split_sentences(text):
	'''
	Utility function to return a list of sentences.
	:param text: the text that must be split in to sentences
	:return: a list of sentences
	'''
	sentence_delimiters = re.compile(u'[.、。!！?？,，;；:：“”\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s ')
	sentences = sentence_delimiters.split(text)
	return sentences

def build_stop_word_regex(stop_word_file_path, min_length = 1, max_length = 3):
	stop_word_list = load_stop_words(stop_word_file_path)
	stop_word_regex_list = []
	for word_regex in stop_word_list:
		if len(word_regex) <= max_length and len(word_regex) >=  min_length:
			stop_word_regex_list.append(word_regex)
	stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
	return stop_word_pattern

def generate_candidate_keywords(sentence_list, stopword_pattern):
	phrase_list = []
	for s in sentence_list:
		tmp = re.sub(stopword_pattern, '|', s.strip())
		phrases = tmp.split("|")
		for phrase in phrases:
			if phrase != "":
				phrase_list.append(phrase)
	return phrase_list

def calculate_word_scores(phraseList):
	word_frequency = {}
	word_degree = {}
	for phrase in phraseList:
		word_list = separate_words(phrase, 0)
		word_list_length = len(word_list)
		word_list_degree = word_list_length - 1
		#if word_list_degree > 3: word_list_degree = 3 #exp.
		for word in word_list:
			word_frequency.setdefault(word, 0)
			word_frequency[word] += 1
			word_degree.setdefault(word, 0)
			word_degree[word] += word_list_degree  #orig.
			#word_degree[word] += 1/(word_list_length*1.0) #exp.
	for item in word_frequency:
		word_degree[item] = word_degree[item] + word_frequency[item]
		# Calculate Word scores = deg(w)/frew(w)
	word_score = {}
	for item in word_frequency:
		word_score.setdefault(item, 0)
		# word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)
		word_score[item] = max(3, word_degree[item] / (word_frequency[item] * 1.0))
	return word_score

def generate_candidate_keyword_scores(phrase_list, word_score):
	keyword_candidates = {}
	kc = []
	for phrase in phrase_list:
		keyword_candidates.setdefault(phrase, 0)
		word_list = separate_words(phrase, 0)
		candidate_score = 0
		for word in word_list:
			candidate_score += word_score[word]
		# keyword_candidates[phrase] = candidate_score
		keyword_candidates[phrase] = candidate_score
	for i, j in keyword_candidates.items():
		kc.append([i,j])
	return kc

def pruning(keywords, word_score):
	for i in range(len(keywords)):
		if len(list(jieba.cut(keywords[i][0], cut_all=False))) != 1 \
				and len(list(jieba.cut(keywords[i][0], cut_all=False))[0]) == 1:
			keywords[i][0] = keywords[i][0][1:]
			keywords[i][1] = keywords[i][1] - word_score[list(jieba.cut(keywords[i][0], cut_all=False))[0]]
		if len(list(jieba.cut(keywords[i][0], cut_all=False))) != 1 \
				and len(list(jieba.cut(keywords[i][0], cut_all=False))[-1]) == 1:
			keywords[i][0] = keywords[i][0][:-1]
			keywords[i][1] = keywords[i][1] - word_score[list(jieba.cut(keywords[i][0], cut_all=False))[-1]]
	for i in range(len(keywords)):
		keywords[i][1] = log(keywords[i][1])
	return keywords

class Rake(object):
	def __init__(self, stop_words_path):
		self.stop_words_path = stop_words_path
		self.__stop_words_pattern = build_stop_word_regex(stop_words_path)

	def run(self, text_file_path):

		text = load_text(text_file_path)

		sentence_list = split_sentences(text)

		phrase_list = generate_candidate_keywords(sentence_list, self.__stop_words_pattern)

		word_scores = calculate_word_scores(phrase_list)

		keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores)

		keyword_candidates = pruning(keyword_candidates, word_scores)

		sorted_keywords = sorted(keyword_candidates, key = lambda x: x[1], reverse = True)
		return sorted_keywords

if __name__ == '__main__':
	# original stop words
	Chinese_stop_words_file = 'Chinese_stop_words.txt'
	# utf-8 text
	Chinese_text_file = 'Chinese_text2.txt'

	key_phrases = Rake(Chinese_stop_words_file).run(Chinese_text_file)

	print(key_phrases)

