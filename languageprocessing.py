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
	for word in stopwords:
		if word in word_dict:
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

		
if __name__ == '__main__':
	word_dict = {"bleh":1}
	save_word_dict(word_dict, "bleh.json")