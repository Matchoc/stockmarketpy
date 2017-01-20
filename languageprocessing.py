import json
import string
from nltk.stem import PorterStemmer

def extract_words(text):
	text = remove_punctuation(text)
	text = text.lower()
	words = text.split()
	ps = PorterStemmer()
	words = [ps.stem(w) for w in words]
	
	ret_dict = {}
	for w in words:
		ret_dict.setdefault(w, 0)
		ret_dict[w] += 1
	return ret_dict

def remove_stopwords(word_dict, stopwords):
	discard = []
	for word in word_dict:
		if word in stopwords or word.isnumeric():
			discard.append(word)
			
	for word in discard:
		del word_dict[word]
			
def remove_punctuation(s):
	exclusions = string.punctuation.join(['\u00bb', '\u2026', '\u201c', '\u201d', '\u2014', '\u2013', '\u2018', '\u2019'])
	#exclusions.extend(string.punctuation)
	table = {ord(c): " " for c in exclusions}
	return s.translate(table)
			
def load_stopwords(path):
	stopwords = set()
	with open(path, 'r') as f:
		for line in f:
			stopwords.add(line.strip())
	return list(stopwords)
	
def save_word_dict(word_dict, path):
	with open(path, 'w') as fo:
		json.dump(word_dict, fo, sort_keys=True,
		indent=4, separators=(',', ': '))

def read_word_dict(file):
	with open(file, 'r') as wordfile:
		return json.load(wordfile)
		
		
def count_all_words(files):
	ret_dict = {}
	for file in files:
		filewords = read_word_dict(file)
		for word in filewords:
			ret_dict.setdefault(word, 0)
			ret_dict[word] += filewords[word]
			
	return ret_dict
	
def cleanup_all_words(all_words):
	discard = []
	for word in all_words:
		num_digit = 0
		if all_words[word] == 1:
			discard.append(word)
			continue
		for l in word:
			if l.isdigit():
				num_digit += 1
		if num_digit > 0.5 * len(word):
			discard.append(word)
	
	for word in discard:
		del all_words[word]
			
		
if __name__ == '__main__':
	word_dict = {"bleh":1}
	save_word_dict(word_dict, "bleh.json")