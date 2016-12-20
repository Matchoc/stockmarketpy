import json
import string

def extract_words(text):
	text = remove_punctuation(text)
	text = text.lower()
	words = text.split()
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
	table = {ord(c): " " for c in string.punctuation}
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
			
		
if __name__ == '__main__':
	word_dict = {"bleh":1}
	save_word_dict(word_dict, "bleh.json")