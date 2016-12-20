import sys
import os
import glob
import operator
import datetime
import dateutil.relativedelta
import win32gui
import win32ui
import win32con
import win32api
import numpy
import json
import csv
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import scipy.ndimage
import multiprocessing
import nltk
from languageprocessing import *
from datageneration import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.externals import joblib
from time import strftime
from time import sleep
from PIL import Image
from sklearn import svm
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import label_ranking_average_precision_score
#import feedparser # seem nice, doesn't import (crash on 'category' key doesn't exist error)

PRINT_LEVEL=1
def myprint(str, level=0):
	if (level >= PRINT_LEVEL):
		print(str)
		
	
def sort_dict(v, asc=True):
	if asc:
		sorted_dict = sorted(v.items(), key=operator.itemgetter(1))
		return sorted_dict
	else:
		pass

def process_news(news, stopwords, filename):
	word_dict = extract_words(news)
	remove_stopwords(word_dict, stopwords)
	save_word_dict(word_dict, filename + ".words")

def process_all_news(symbol):
	stop_words = load_stopwords('./stopwords.txt')
	
	with open(get_news_json_path(symbol), 'r') as jsonfile:
		newslist = json.load(jsonfile)
		
	for news in newslist:
		title = news["title"]
		content = ""
		if "contents" in news and news["contents"] is not None:
			content = news["contents"]
		process_news(title, stop_words, content)
	
def generate_word_counts():
	wordglob = os.path.join(DATA_FOLDER, "**", "*.words")
	wordfiles = glob.glob(wordglob)
	all_words = count_all_words(wordfiles)
	
	allwordspath = os.path.join(DATA_FOLDER, "allwords.json")
	with open(allwordspath, 'w') as fo:
		json.dump(all_words, fo, sort_keys=True,
		indent=4, separators=(',', ': '))
		
	return all_words
	
def gen_news_x(news):
	allwordspath = os.path.join(DATA_FOLDER, "allwords.json")
	with open(allwordspath, 'r') as jsonfile:
		allwords = json.load(jsonfile)
	newswordspath = news["contents"] + ".words"
	with open(newswordspath, 'r') as jsonfile:
		newswords = json.load(jsonfile)
	sortedX = sorted(allwords.keys())
	x = []
	for key in sortedX:
		count = 0
		if key in newswords:
			count += newswords[key]
		x.append(count)
	return x
	
def get_valid_market_date(newsdate):
	if newsdate.weekday() == 5 or newsdate.weekday() == 6:
		next_monday = datetime.datetime.now() + dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.MO(1))
		return next_monday
	return newsdate

def gen_news_y(symbol, news):
	pubdatestr = news["pubDate"]
	# sample : "Fri, 16 Dec 2016 16:18:35 GMT"
	result = datetime.datetime.strptime(pubdatestr, '%a, %d %b %Y %H:%M:%S %Z').date()
	result = get_valid_market_date(result)
	csvpath = get_price_csv_path(symbol)
	jsonpath = csvpath.replace(".csv", ".json")
	with open(jsonpath, 'r') as jsonfile:
		prices = json.load(jsonfile)
	pricedatefmt = result.strftime("%Y-%m-%d")
	#pricedatefmt = str(year) + "-" + str(month) + "-" + str(day)
	if pricedatefmt in prices:
		price = prices[pricedatefmt]
		y = (price["Close"] - price["Open"]) / price["Open"]
		return y
	return None

def gatherTraining(symbol):
	newspath = get_news_json_path(symbol)
	with open(newspath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
	all_x = []
	all_y = []
	count = 0
	for news in allnews:
		x = gen_news_x(news)
		y = gen_news_y("BNS", news)
		if y is not None:
			all_x.append(x)
			all_y.append(y)
		else:
			myprint("failed to load : " + str(count), 1)
		count += 1
			
	return all_x, all_y

def train_machine():
	myprint("Start machine training...", 1)
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		symbols = json.load(jsonfile)
	
	all_x = []
	all_y = []
	for symbol in symbols:
		cur_x, cur_y = gatherTraining(symbol)
		all_x += cur_x
		all_y += cur_y
		
	all_x = numpy.array(all_x)
		
	#all_x, all_y = gatherTraining()
	#MACHINE_ALL = MLPRegressor(solver='lbgfs', alpha=10.0, hidden_layer_sizes=(150, 29), random_state=1000, activation="relu", max_iter=4000, batch_size=590)
	MACHINE_ALL = MLPRegressor(solver='lbgfs', alpha=10.0, hidden_layer_sizes=(150, 29))
	#SCALER = StandardScaler()
	#SCALER.fit(all_x)
	#all_x = SCALER.transform(all_x)
	myprint(all_x,1)
	MACHINE_ALL.fit(all_x, all_y)
	myprint("... End machine training", 1)
	myprint("all_y: " + str(all_y), 0)
	
	newspath = get_news_json_path("BNS")
	with open(newspath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
	x = gen_news_x(allnews[80])
	#x = SCALER.transform(x)
	res = MACHINE_ALL.predict(x)
	myprint("res : " + str(res), 1)
	myprint("calculated from x : " + str(x), 0)
	
		
def update_symbol(symbol, steps):
	symboldir = os.path.join(DATA_FOLDER, symbol)
	if not os.path.isdir(symboldir):
		os.makedirs(symboldir)
	if "dlprice" in steps:
		csvpath = download_year_prices(symbol)
	if "dlrss" in steps or "rss2json" in steps:
		rsspath = download_yahoo_rss(symbol)
	if "price2json" in steps:
		pricejson = convert_prices_to_json(symbol)
	if "rss2json" in steps:
		newsjson = convert_yahoorss_to_json(symbol, rsspath)
	if "dlnews" in steps:
		download_all_news_page(symbol)
	if "processnews" in steps:
		process_all_news(symbol)

def update_all_symbols(steps=["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews"]):
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		links = json.load(jsonfile)
	
	for symbol in links:
		update_symbol(symbol, steps)
	
if __name__ == '__main__':
	#update_symbol("BNS")
	update_all_symbols(["processnews"])
	ret = generate_word_counts()
	#myprint(sort_dict(ret), 1)
	train_machine()
	
	myprint("done", 5)