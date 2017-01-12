import sys
import os
os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"]
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
import matplotlib.pyplot as plt
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

SKIP_SYMBOL = "" # for debugging one symbol skip training of this one (different than cross-validating which should take a random sample... in this case I want to debug a specific symbol)

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

def get_news_date(news):
	if type(news) is dict:
		pubdatestr = news["pubDate"]
	else:
		pubdatestr = news
	result = datetime.datetime.strptime(pubdatestr, '%a, %d %b %Y %H:%M:%S %Z')
	return result
	
def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
	
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
	
	# skip news we couldn't download
	with open(news["contents"], 'rb') as testfo:
		text = testfo.read()
	if len(text) <= 0:
		return None
		
	with open(newswordspath, 'r') as jsonfile:
		newswords = json.load(jsonfile)
	sortedX = sorted(allwords.keys())
	#price = get_close_prev_day(symbol, news)
	x = get_base_X(symbol, news)
	#x = []
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
	
def gen_allnews_x(symbol, allnews):
	allwordspath = os.path.join(DATA_FOLDER, "allwords.json")
	with open(allwordspath, 'r') as jsonfile:
		allwords = json.load(jsonfile)
	sortedX = sorted(allwords.keys())
	x = get_base_X(symbol, allnews[0])
	x_words = [0] * len(sortedX)
	valid_news = False
	for news in allnews:
		newswordspath = news["contents"] + ".words"
		# skip news we couldn't download
		with open(news["contents"], 'rb') as testfo:
			text = testfo.read()
		if len(text) <= 0:
			continue
		with open(newswordspath, 'r') as jsonfile:
			newswords = json.load(jsonfile)
		
		count = 0
		for key in sortedX:
			if key in newswords:
				x_words[count] += newswords[key]
				#x_words[count] = 1
			count += 1
		valid_news = True
	x = x + x_words
	if valid_news:
		return [x]
	else:
		return None
	
def get_base_X(symbol, news):
	prev_close_price = get_previous_close_price(symbol, news)
	avg_price_week = calculate_average_price_over_time(symbol, news, datetime.timedelta(weeks=1))
	avg_price_month = calculate_average_price_over_time(symbol, news, datetime.timedelta(weeks=4))
	avg_price_year = calculate_average_price_over_time(symbol, news, datetime.timedelta(weeks=52))
	days_up = get_num_days_up(symbol, news)
	
	x = [prev_close_price, avg_price_week, avg_price_month, avg_price_year, days_up]
	myprint(symbol + " : " + news["title"] + " prev close, avg week, avg month, avg year = " + str(x))
	return x
	
def get_price_date(pricejson, lookupdate):
	pricedatefmt = lookupdate.strftime("%Y-%m-%d")
	if pricedatefmt in pricejson:
		return pricejson[pricedatefmt]
	return None
	
def get_num_days_up(symbol, news):
	newsdate = get_news_date(news)
	pricejson = get_price_json(symbol)
	prev_day = newsdate - datetime.timedelta(days=1)
	price = get_price_date(pricejson, prev_day)
	while price is None and (newsdate - prev_day).days < 365:
		prev_day = prev_day - datetime.timedelta(days=1)
		price = get_price_date(pricejson, prev_day)
	if price is None:
		myprint("Could not find any valid date in get_num_days_up : " + symbol + " for news : " + news["title"], 5)
		return 0
	isPositive = price["Adj Close"] - price["Open"] >= 0
	curPositive = price["Adj Close"] - price["Open"] >= 0
	count = 1
	while (price is None and (newsdate - prev_day).days < 365) or (isPositive == curPositive):
		prev_day = prev_day - datetime.timedelta(days=1)
		price = get_price_date(pricejson, prev_day)
		
		if price is not None:
			count += 1
			curPositive = price["Adj Close"] - price["Open"] >= 0
		else:
			curPositive = not isPositive
		
	if not isPositive:
		count = count * -1
	
	return count
	
def calculate_average_price_over_time(symbol, news, delta):
	csvpath = get_price_csv_path(symbol)
	jsonpath = csvpath.replace(".csv", ".json")
	with open(jsonpath, 'r') as jsonfile:
		prices = json.load(jsonfile)
	
	news_date = get_news_date(news)
	start_date = news_date - delta
	cur_date = start_date
	avg_close_price = 0
	count = 0
	while cur_date < news_date:
		pricedatefmt = cur_date.strftime("%Y-%m-%d")
		if pricedatefmt in prices:
			avg_close_price += prices[pricedatefmt]["Adj Close"]
			count += 1
		cur_date += datetime.timedelta(days=1)
		
	if count > 0:
		avg_close_price = avg_close_price / count
		
	return avg_close_price
	
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
	
def get_previous_close_price(symbol, news):
	csvpath = get_price_csv_path(symbol)
	jsonpath = csvpath.replace(".csv", ".json")
	with open(jsonpath, 'r') as jsonfile:
		prices = json.load(jsonfile)
	
	result = get_news_date(news)
	result = get_valid_market_date(result)
	result = result - datetime.timedelta(days=1)
	if result.weekday() == 5 or result.weekday() == 6:
		result = result + dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.FR(-1))
	
	pricedatefmt = result.strftime("%Y-%m-%d")
	try:
		while pricedatefmt not in prices:
			result = result - datetime.timedelta(days=1)
			pricedatefmt = result.strftime("%Y-%m-%d")		
	except OverflowError as e:
		final_price = 10

	if pricedatefmt in prices:
		final_price = prices[pricedatefmt]["Adj Close"]
		
	return final_price

def gen_news_y(symbol, news):
	# sample : "Fri, 16 Dec 2016 16:18:35 GMT"
	result = get_news_date(news)
	result = get_valid_market_date(result)
	csvpath = get_price_csv_path(symbol)
	jsonpath = csvpath.replace(".csv", ".json")
	with open(jsonpath, 'r') as jsonfile:
		prices = json.load(jsonfile)
	pricedatefmt = result.strftime("%Y-%m-%d")
	#pricedatefmt = str(year) + "-" + str(month) + "-" + str(day)
	if pricedatefmt in prices:
		price = prices[pricedatefmt]
		y = (price["Adj Close"] - price["Open"])# / price["Open"]
		return y
	return None

def get_close_prev_day(symbol, news):
	# sample : "Fri, 16 Dec 2016 16:18:35 GMT"
	result = get_news_date(news)
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
	return price["Adj Close"]
	
def group_news_by_date(allnews):
	results = {}
	for news in allnews:
		newsdate = get_news_date(news)
		newsdate = get_valid_market_date(newsdate)
		pricedatefmt = newsdate.strftime("%Y-%m-%d")
		if pricedatefmt not in results:
			results[pricedatefmt] = []
		results[pricedatefmt].append(news)
		
	return results
	
def updateTraining_by_date(symbol):
	newspath = get_news_json_path(symbol)
	with open(newspath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
	all_x = []
	all_y = []
	all_news = []
	failedx = 0
	failedy = 0
	news_by_date = group_news_by_date(allnews)
	for key in news_by_date:
		y = gen_news_y(symbol, news_by_date[key][0])
		if y is not None:
			x = gen_allnews_x(symbol, news_by_date[key])
			if x is not None:
				all_x += x
				all_y.append(y)
				all_news.append(news_by_date[key]) # useful for debugging
			else:
				failedx += 1
				myprint("[" + symbol + "] failed to load news X (" + news_by_date[key][0]["pubDate"] + ")", 1)
		else:
			failedy += 1
			myprint("[" + symbol + "] failed to load news y (" + news_by_date[key][0]["pubDate"] + ")", 1)
			
		myprint("[" + symbol + "] processed " + news_by_date[key][0]["pubDate"] + " with " + str(len(news_by_date[key])) + " news", 0)
			
	myprint("Failed to load " + str(failedx) + " X and " + str(failedy) + "Y on a list of " + str(len(news_by_date)) + " dates", 2)
	results = {}
	results["X"] = all_x
	results["y"] = all_y
	results["news"] = all_news
	with open(get_training_json(symbol), 'w') as fo:
		json.dump(results, fo, sort_keys=True,
		indent=4, separators=(',', ': '))
	return all_x, all_y
	
def updateTraining(symbol):
	newspath = get_news_json_path(symbol)
	with open(newspath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
	all_x = []
	all_y = []
	all_news = []
	failedx = 0
	failedy = 0
	for news in allnews:
		y = gen_news_y(symbol, news)
		if y is not None:
			x = gen_news_x(symbol, news)
			if x is not None:
				all_x += x
				all_y.append(y)
				all_news.append(news) # useful for debugging
			else:
				failedx += 1
				myprint("[" + symbol + "] failed to load news X : " + news["title"] + " (" + news["pubDate"] + ")", 1)
		else:
			failedy += 1
			myprint("[" + symbol + "] failed to load news y : " + news["title"] + " (" + news["pubDate"] + ")", 1)
			
	myprint("Failed to load " + str(failedx) + " X and " + str(failedy) + "Y", 1)
	results = {}
	results["X"] = all_x
	results["y"] = all_y
	results["news"] = all_news
	with open(get_training_json(symbol), 'w') as fo:
		json.dump(results, fo, sort_keys=True,
		indent=4, separators=(',', ': '))
	return all_x, all_y
	
def gatherTraining(symbol):
	trainingjsonpath = get_training_json(symbol)
	if not os.path.isfile(trainingjsonpath):
		return updateTraining_by_date(symbol)
	
	with open(trainingjsonpath, 'r') as jsonfile:
		trainingjson = json.load(jsonfile)
		
	return trainingjson

def get_all_Xy():
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		symbols = json.load(jsonfile)
		
	data = {}
	all_x = []
	all_y = []
	for symbol in symbols:
		if SKIP_SYMBOL == symbol:
			continue
		training_data = gatherTraining(symbol)
		cur_x, cur_y = training_data["X"], training_data["y"]
		all_x += cur_x
		all_y += cur_y
	data["X"] = all_x
	data["y"] = all_y
	return data
	
def train_machine(data, alpha, hidden_layer_sizes):
	global MACHINE_NEWS
	global SCALER_NEWS
	all_x = data["X"]
	all_y = data["y"]
	myprint("Start machine training (alpha=" + str(alpha) + ", layers = " + str(hidden_layer_sizes) + ")...", 3)
	MACHINE_NEWS = MLPRegressor(solver='lbgfs', alpha=alpha, hidden_layer_sizes=hidden_layer_sizes, random_state=1000, activation="relu", max_iter=2000, verbose=False)
	#MACHINE_NEWS = MLPRegressor(solver='lbgfs', alpha=0.005, hidden_layer_sizes=(150, 29), random_state=1000, activation="relu", max_iter=400000, batch_size=590)
	SCALER_NEWS = StandardScaler()
	SCALER_NEWS.fit(all_x)
	all_x = SCALER_NEWS.transform(all_x)
	MACHINE_NEWS.fit(all_x, all_y)
	save_machine()
	myprint("... End machine training : loss " + str(MACHINE_NEWS.loss_) + ", iter " + str(MACHINE_NEWS.n_iter_), 3)
	
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
		res_per = res
		expected_per = data["y"][count]
		myprint("predicted value : " + str(res_per) + ", real answer : " + str(expected_per) + " ecart : " + str(abs(expected_per - res_per)), 2)
		avg_ecart += abs(expected_per - res_per)
		root_mean_square += (expected_per - res_per)**2
		count += 1
	
	root_mean_square = (root_mean_square/count)**0.5
	myprint("avg ecart : " + str(avg_ecart / count) + ", root mean square : " + str(root_mean_square), 4)
		
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
	if "updateTraining" in steps:
		updateTraining_by_date(symbol)

def update_all_symbols(steps=["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "allwords", "updateTraining", "train", "crossval", "today"]):
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
		train_machine(data, 25.0, (180,30))
		
	if "crossval" in steps:
		passed_data = {}
		passed_data["X"] = data["X"][int(len(data["X"]) * per):]
		passed_data["y"] = data["y"][int(len(data["X"]) * per):]
		cross_validate(data)
		
	if "today" in steps:
		predict_all_today()
		
def train_cross_variations():
	alphas = [0.000005, 0.00005, 0.005, 0.5, 25.0]
	hiddens = [(150, 29), (180, 30), (150, 150), (350, 350), (100, 100), (175,175), (150,150,150)]
	
	data = get_all_Xy()
	per = 0.8
	myprint("crossvalidating : training size = " + str(int(len(data["X"]) * per)) + ", validation size = " + str(int(len(data["X"]) * (1 - per))), 4)
	#for alpha in alphas:
	#	passed_data = {}
	#	passed_data["X"] = data["X"][:int(len(data["X"]) * per)]
	#	passed_data["y"] = data["y"][:int(len(data["y"]) * per)]
	#	train_machine(data, alpha, (150,29))
	#	passed_data = {}
	#	passed_data["X"] = data["X"][int(len(data["X"]) * per):]
	#	passed_data["y"] = data["y"][int(len(data["X"]) * per):]
	#	cross_validate(data)
	#	myprint("------------------------",3)
	
	main_data = {}
	main_data["X"] = data["X"][:int(len(data["X"]) * per)]
	main_data["y"] = data["y"][:int(len(data["y"]) * per)]
	validation_data = {}
	validation_data["X"] = data["X"][int(len(data["X"]) * per):]
	validation_data["y"] = data["y"][int(len(data["X"]) * per):]
	for alpha in alphas:
		for hidden in hiddens:
			train_machine(main_data, alpha, hidden)
			cross_validate(validation_data)
			myprint("------------------------", 4)
	
def get_most_recent_news_X(symbol, data):
	newspath = get_news_json_path(symbol)
	with open(newspath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
	
	most_recent_news = None
	most_recent_news_date = None
	for news in allnews:
		result = get_news_date(news)
		if most_recent_news is None:
			most_recent_news = news
			most_recent_news_date = result
		else:
			if result > most_recent_news_date:
				most_recent_news = news
				most_recent_news_date = result
				
	myprint("predict " + symbol + " Using : '" + most_recent_news["title"] + "' (" + most_recent_news["pubDate"] + ")", 2)
	x = []
	res = gen_news_x(symbol, most_recent_news)
	if res is not None:
		x += res
	data["news"] = most_recent_news
	data["symbol"] = symbol
		
	return x
			
	
def get_today_X(symbol):
	newspath = get_news_json_path(symbol)
	with open(newspath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
	
	valid_news = []
	last_valid_date = datetime.datetime.now()
	last_valid_date = get_valid_market_date(last_valid_date)
	for news in allnews:
		result = get_news_date(news)
		result = get_valid_market_date(result)
		if result >= last_valid_date:
			valid_news.append(news)
	
	x = []
	for news in valid_news:
		res = gen_news_x(symbol, news)
		if res is not None:
			x += res
		
	return x
	
def predict_all_today():
	if MACHINE_NEWS is None:
		load_machine()
		
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		symbols = json.load(jsonfile)
		
	results = []
	for symbol in symbols:
		data = {}
		#x = get_today_X(symbol)
		x = get_most_recent_news_X(symbol, data)
		if len(x) == 0:
			myprint("Skip " + symbol + " no date for today")
			continue
		x = SCALER_NEWS.transform(x)
		data["result"] = MACHINE_NEWS.predict(x)
		results.append(data)
	
	#myprint(results, 5)
	reorder_and_print_results(results)
	
def reorder_and_print_results(results):
	sorted_results = sorted(results, key=lambda k: k['result'])
	result_dir = os.path.join(DATA_FOLDER, "predictions")
	if not os.path.isdir(result_dir):
		os.makedirs(result_dir)
		
	timestr = strftime("%Y%m%d-%H%M%S")
	pathcsv = os.path.join(result_dir, "prediction-" + timestr + ".csv")
	
	with open(pathcsv, 'w') as f:
		title = []
		title.append("symbol")
		title.append("prediction $")
		title.append("prediction %")
		title.append("last close")
		title.append("pudDate")
		title.append("pudTime")
		title.append("title")
		f.write(";".join(title) + "\n")
		for result in sorted_results:
			line = []
			line.append(result["symbol"])
			last_close_price = get_previous_close_price(result["symbol"], result["news"])
			line.append(str(result["result"][0]))
			line.append(str(result["result"][0] / last_close_price * 100.0))
			line.append(str(last_close_price))
			pubdate = get_news_date(result["news"]["pubDate"])
			pubdate = utc_to_local(pubdate)
			line.append(pubdate.strftime("%Y-%m-%d"))
			line.append(pubdate.strftime("%H:%M:%S"))
			line.append(result["news"]["title"])
			f.write(";".join(line) + "\n")
	
def print_ordered_all_words():
	allwordspath = os.path.join(DATA_FOLDER, "allwords.json")
	with open(allwordspath, 'r') as jsonfile:
		allwords = json.load(jsonfile)
	
	sorted_words = sort_dict(allwords)
	for word in sorted_words:
		sys.stdout.buffer.write((str(word) + "\n").encode('UTF-8'))
	
def graph_actual_vs_predicted():
	if MACHINE_NEWS is None:
		load_machine()
	data = get_all_Xy() # SKIP_SYMBOL should be set and training should have been done with same skip_symbol (unless testing overfitting)
	skipped_data = gatherTraining(SKIP_SYMBOL)
	skipDataX, realresult, allnews = skipped_data["X"], skipped_data["y"], skipped_data["news"]
	predictedresult = []
	count = 0
	sx = SCALER_NEWS.transform(skipDataX)
	predictedresult = MACHINE_NEWS.predict(sx)
	
	dates = [get_news_date(news[0]) for news in allnews]
	
	result = []
	count = 0
	
	result = [{'date': dates[i], 'pred': predictedresult[i], 'real': realresult[i]} for i in range(len(dates))]
	
	sorted_results = sorted(result, key=lambda k: k['date'])
	
	sorted_preds = [k['pred'] for k in sorted_results]
	sorted_dates = [k['date'] for k in sorted_results]
	sorted_real = [k['real'] for k in sorted_results]
	
	plt.plot(sorted_dates, sorted_preds, 'ro-', label="predicted", linewidth=2)
	plt.plot(sorted_dates, sorted_real, 'bo-', label="actual", linewidth=2)
	
	csvpath = get_price_csv_path(SKIP_SYMBOL)
	jsonpath = csvpath.replace(".csv", ".json")
	with open(jsonpath, 'r') as jsonfile:
		prices = json.load(jsonfile)
	data = []
	for key in prices:
		day_price = {}
		day_price["date"] = datetime.datetime.strptime(key, '%Y-%m-%d')
		day_price["pl"] = prices[key]["Adj Close"] - prices[key]["Open"]
		data.append(day_price)
	all_prices = sorted(data, key=lambda k: k['date'])
	prices_date = [k["date"] for k in all_prices]
	prices_pl = [k["pl"] for k in all_prices]
	plt.plot(prices_date, prices_pl, 'go-', label="all prices")
	plt.axhline(0)
	plt.legend()
	
	plt.show()
	
	myprint("todo")
	
if __name__ == '__main__':
	#train_cross_variations()
	#graph_actual_vs_predicted()
	#update_symbol("BNS")
	
	# Update everything (word list, training, news, all the bang)
	#update_all_symbols(["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "allwords", "updateTraining", "train"])
	
	# Update news and do a prediction based only on previous training and word list (don't update word list or machine)
	update_all_symbols(["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "today"])
	
	# Update everything and do a cross-validation check (will printout a square mean variation)
	#update_all_symbols(["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "allwords", "updateTraining", "train", "crossval"])
	
	#update_all_symbols(["processnews", "allwords", "updateTraining", "train"])
	#update_all_symbols(["updateTraining"])
	#update_all_symbols(["price2json", "rss2json"])
	#update_all_symbols(["dlnews", "processnews"])
	#update_all_symbols(["processnews", "allwords"])
	#update_all_symbols(["allwords"])
	#update_all_symbols(["updateTraining", "train"])
	#update_all_symbols(["train"])
	#update_all_symbols(["train", "crossval"])
	#update_all_symbols(["crossval"])
	#update_all_symbols(["today"])
	
	myprint("done", 5)