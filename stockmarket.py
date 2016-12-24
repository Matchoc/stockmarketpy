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

MACHINE_NEWS = None
SCALER_NEWS = None

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
		
def save_machine():
	joblib.dump(MACHINE_NEWS, 'machine_news.save')
	joblib.dump(SCALER_NEWS, 'scaler_news.save')
		
def load_machine():
	global MACHINE_NEWS
	global SCALER_NEWS
	MACHINE_NEWS = joblib.load('machine_news.save')
	SCALER_NEWS = joblib.load('scaler_news.save')

def process_news(news, stopwords, filename):
	newscontent = " "
	if filename is not "":
		newscontent += get_important_text_from_news(filename)
	word_dict = extract_words(news + newscontent)
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
	
def gen_news_x(symbol, news):
	allwordspath = os.path.join(DATA_FOLDER, "allwords.json")
	with open(allwordspath, 'r') as jsonfile:
		allwords = json.load(jsonfile)
	newswordspath = news["contents"] + ".words"
	with open(newswordspath, 'r') as jsonfile:
		newswords = json.load(jsonfile)
	sortedX = sorted(allwords.keys())
	#price = get_close_prev_day(symbol, news)
	x = []
	for key in sortedX:
		count = 0
		if key in newswords:
			count += newswords[key]
		#if count > 0:
		#	x.append(1)
		#else:
		#	x.append(0)
		x.append(count)
	return [x]
	
def get_valid_market_date(newsdate):
	offset = 0
	if newsdate.time().utcoffset() is not None:
		offset = newsdate.time().utcoffset()
	offset -= 5 # toronto stock time zone
	finaldate = newsdate + datetime.timedelta(hours=offset)
	if finaldate.hour >= 16:
		finaldate = finaldate + datetime.timedelta(days=1)
		myprint(str(newsdate) + " is  after 16 so going to use : " + str(finaldate), 0)
	if finaldate.weekday() == 5 or finaldate.weekday() == 6:
		myprint(str(finaldate) + " is  a " + str(finaldate.weekday()), 0)
		finaldate = finaldate + dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.MO(1))
	myprint("final date = " + str(finaldate), 0)
	return finaldate

def gen_news_y(symbol, news):
	pubdatestr = news["pubDate"]
	# sample : "Fri, 16 Dec 2016 16:18:35 GMT"
	result = datetime.datetime.strptime(pubdatestr, '%a, %d %b %Y %H:%M:%S %Z')
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

def get_close_prev_day(symbol, news):
	pubdatestr = news["pubDate"]
	# sample : "Fri, 16 Dec 2016 16:18:35 GMT"
	result = datetime.datetime.strptime(pubdatestr, '%a, %d %b %Y %H:%M:%S %Z')
	result = get_valid_market_date(result)
	result = result - datetime.timedelta(days=1)
	csvpath = get_price_csv_path(symbol)
	jsonpath = csvpath.replace(".csv", ".json")
	with open(jsonpath, 'r') as jsonfile:
		prices = json.load(jsonfile)
	pricedatefmt = result.strftime("%Y-%m-%d")
	#pricedatefmt = str(year) + "-" + str(month) + "-" + str(day)
	if pricedatefmt in prices:
		price = prices[pricedatefmt]
	return price["Close"]
	
def gatherTraining(symbol):
	newspath = get_news_json_path(symbol)
	with open(newspath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
	all_x = []
	all_y = []
	count = 0
	for news in allnews:
		x = gen_news_x(symbol, news)
		y = gen_news_y(symbol, news)
		if y is not None:
			all_x += x
			all_y.append(y)
		else:
			myprint("[" + symbol + "] failed to load news index " + str(count) + " : " + news["title"], 1)
		count += 1
			
	return all_x, all_y

def get_all_Xy():
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		symbols = json.load(jsonfile)
		
	data = {}
	all_x = []
	all_y = []
	for symbol in symbols:
		cur_x, cur_y = gatherTraining(symbol)
		all_x += cur_x
		all_y += cur_y
	data["X"] = all_x
	data["y"] = all_y
	return data
	
def train_machine(data):
	global MACHINE_NEWS
	global SCALER_NEWS
	all_x = data["X"]
	all_y = data["y"]
	myprint("Start machine training...", 1)
	MACHINE_NEWS = MLPRegressor(solver='lbgfs', alpha=0.005, hidden_layer_sizes=(150, 29), random_state=1000, activation="relu", max_iter=400000, batch_size=590)
	SCALER_NEWS = StandardScaler()
	SCALER_NEWS.fit(all_x)
	all_x = SCALER_NEWS.transform(all_x)
	MACHINE_NEWS.fit(all_x, all_y)
	save_machine()
	myprint("... End machine training", 1)
	
	newspath = get_news_json_path("S")
	with open(newspath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
		
def cross_validate(data):
	if MACHINE_NEWS is None:
		load_machine()
	x = data["X"]
	x = SCALER_NEWS.transform(x)
	results = MACHINE_NEWS.predict(x)
	count = 0
	avg_ecart = 0
	root_mean_square = 0
	for res in results:
		res_per = res * 100
		expected_per = data["y"][count] * 100
		myprint("predicted value : " + str(res_per) + "%, real answer : " + str(expected_per) + "% ecart : " + str(abs(expected_per - res_per)), 2)
		avg_ecart += abs(expected_per - res_per)
		root_mean_square += (expected_per - res_per)**2
		count += 1
	
	root_mean_square = (root_mean_square/count)**0.5
	myprint("avg ecart : " + str(avg_ecart / count) + ", root mean square : " + str(root_mean_square), 2)
		
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

def update_all_symbols(steps=["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "allwords", "train", "crossval", "today"]):
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		links = json.load(jsonfile)
	
	for symbol in links:
		update_symbol(symbol, steps)
		
	if "allwords" in steps:
		ret = generate_word_counts()
		myprint(sort_dict(ret), 0)
		
	per = 1.0
	if "crossval" in steps or "train" in steps:
		data = get_all_Xy()
		
	if "crossval" in steps:
		per = 0.7
		myprint("crossvalidating : training size = " + str(int(len(data["X"]) * per)) + ", validation size = " + str(int(len(data["X"]) * (1 - per))), 2)
		
	if "train" in steps:
		passed_data = {}
		passed_data["X"] = data["X"][:int(len(data["X"]) * per)]
		passed_data["y"] = data["y"][:int(len(data["y"]) * per)]
		train_machine(data)
		
	if "crossval" in steps:
		passed_data = {}
		passed_data["X"] = data["X"][int(len(data["X"]) * per):]
		passed_data["y"] = data["y"][int(len(data["X"]) * per):]
		cross_validate(data)
		
	if "today" in steps:
		predict_all_today()
		
def get_today_X(symbol):
	newspath = get_news_json_path(symbol)
	with open(newspath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
	
	valid_news = []
	for news in allnews:
		pubdatestr = news["pubDate"]
		result = datetime.datetime.strptime(pubdatestr, '%a, %d %b %Y %H:%M:%S %Z')
		result = get_valid_market_date(result)
		if result >= datetime.datetime.now():
			valid_news.append(news)
	
	x = []
	for news in valid_news:
		x += gen_news_x(symbol, news)
		
	return x
	
def predict_all_today():
	if MACHINE_NEWS is None:
		load_machine()
		
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		symbols = json.load(jsonfile)
		
	results = {}
	for symbol in symbols:
		x = get_today_X(symbol)
		if len(x) == 0:
			myprint("Skip " + symbol + " no date for today")
			continue
		x = SCALER_NEWS.transform(x)
		results[symbol] = MACHINE_NEWS.predict(x)
		
	myprint(results, 5)
	
if __name__ == '__main__':
	#update_symbol("BNS")
	#update_all_symbols(["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "allwords", "train"])
	#update_all_symbols(["price2json", "rss2json"])
	#update_all_symbols(["dlnews", "processnews"])
	#update_all_symbols(["processnews", "allwords"])
	#update_all_symbols(["allwords"])
	#update_all_symbols(["train", "crossval"])
	update_all_symbols(["crossval"])
	#update_all_symbols(["today"])
	#myprint(sort_dict(ret), 1)
	#get_important_text_from_news(r"G:\Perso\projects\stockmarketpy\data\BCE\20161218-220023.news")
	#update_all_symbols([
	#	"processnews",
	#	"allwords"
	#	])
	

	
	myprint("done", 5)