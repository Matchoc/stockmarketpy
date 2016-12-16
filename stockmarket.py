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
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.externals import joblib
from time import strftime
from time import sleep
from PIL import Image
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import label_ranking_average_precision_score
#import feedparser # seem nice, doesn't import (crash on 'category' key doesn't exist error)

RSS_FEED_FILENAME = "news_link.json"
DATA_FOLDER = "data"
PROCESS_DATA = "data\\processed_data.json"

PRINT_LEVEL=1
def myprint(str, level=0):
	if (level >= PRINT_LEVEL):
		print(str)
		
def downloadURL(url):
	try:
		req = urllib.request.Request(url)
		req.add_header('Referer', 'http://us.rd.yahoo.com/')
		req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.1 \
				  (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1')
		resp = urllib.request.urlopen(req)
		data = resp.read()
		#response = urllib.request.urlopen(url)
		#data = response.read()      # a `bytes` object
		myprint(data,0)
		text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
	except urllib.error.HTTPError as e:
		myprint("URL failed : " + str(e.code) + " " + e.reason, 5)
		return ""
	except UnicodeDecodeError as e:
		myprint("URL failed : Response not unicode", 5)
		return ""
	return text


# I NEED TO USE lastBuildDate IN THE NEWS RSS FEED OF YAHOO IF I WANT MY DATA TO BE MEANINGFUL !
		
def get_latest_stock_date():
	today = datetime.date.today()# - datetime.timedelta(days=1)
	month = today.month
	year = today.year
	day = today.day
	
	if today.weekday() == 5 or today.weekday() == 6:
		lastfriday = datetime.datetime.now() + dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.FR(-1))
		month = lastfriday.month
		year = lastfriday.year
		day = lastfriday.day
		
	return {"month":month, "year":year, "day":day}
		
def update_52_prices():
	#end, start
	#month, day, year, month, day, year
	#11 3 2016 0 12 1995 
	#&d=11&e=3&f=2016&g=d&a=0&b=12&c=1995
	
	stockdate = get_latest_stock_date()
	month = stockdate["month"]
	day = stockdate["day"]
	year = stockdate["year"]
	dateparam = "&d={}&e={}&f={}&g=d&a={}&b={}&c={}".format(month-1, day, year, month-1, day, year-1)
	
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		links = json.load(jsonfile)
	for symbol in links:
		url = links[symbol]["prices"]
		url += dateparam
		myprint("get price : " + url,1)
		text = downloadURL(url)
		if text == None:
			myprint("Price list empty", 5)
		
		#timestr = "-{year}{month:02d}{day:02d}".format(year=year, month=month, day=day)
		csvpath = os.path.join(DATA_FOLDER, symbol + "-price" + ".csv")
		with open(csvpath, 'w') as csvfile:
			csvfile.write(text)

def parse_csv_date(datestr):
	datetime_object = datetime.strptime('2016-12-15', '%Y-%m-%d')
	return datetime_object
			
def pricecsv_to_json():
	priceglob = os.path.join(DATA_FOLDER, "*-price.csv")
	pricefiles = glob.glob(priceglob)
	for pricefile in pricefiles:
		finaljson = {}
		with open(pricefile, newline='') as csvfile:
			priceinfo = {}
			csvreader = csv.reader(csvfile, delimiter=',')
			info = next(csvreader, None)  # skip the headers
			while info is not None:
				info = next(csvreader, None)
				if info == None:
					break
				finaljson[info[0]] = {}
				finaljson[info[0]]["Open"] = float(info[1])
				finaljson[info[0]]["High"] = float(info[2])
				finaljson[info[0]]["Low"] = float(info[3])
				finaljson[info[0]]["Close"] = float(info[4])
				finaljson[info[0]]["Volume"] = float(info[5])
				finaljson[info[0]]["Adj Close"] = float(info[6])

		with open(pricefile + ".json", 'w') as fo:
			json.dump(finaljson, fo, sort_keys=True,
			indent=4, separators=(',', ': '))
		
def update_prices():
	#end, start
	#month, day, year, month, day, year
	#11 3 2016 0 12 1995 
	#&d=11&e=3&f=2016&g=d&a=0&b=12&c=1995
	
	stockdate = get_latest_stock_date()
	month = stockdate["month"]
	day = stockdate["day"]
	year = stockdate["year"]
	dateparam = "&d={}&e={}&f={}&g=d&a={}&b={}&c={}".format(month-1, day, year, month-1, day, year)
	
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		links = json.load(jsonfile)
	for symbol in links:
		url = links[symbol]["prices"]
		url += dateparam
		myprint("get price : " + url,1)
		text = downloadURL(url)
		if text == None:
			myprint("Price list empty", 5)
		
		timestr = "-{year}{month:02d}{day:02d}".format(year=year, month=month, day=day)
		csvpath = os.path.join(DATA_FOLDER, symbol + timestr + ".csv")
		with open(csvpath, 'w') as csvfile:
			csvfile.write(text)
		
def update_news():
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		links = json.load(jsonfile)
	
	stockdate = get_latest_stock_date()
	month = stockdate["month"]
	day = stockdate["day"]
	year = stockdate["year"]
	
	for symbol in links:
		timestr = "-{year}{month:02d}{day:02d}".format(year=year, month=month, day=day)
		xmlpath = os.path.join(DATA_FOLDER, symbol + timestr + ".xml")
		if os.path.isfile(xmlpath):
			continue
			
		url = links[symbol]["news"]
		myprint("get news : " + url,1)
		text = downloadURL(url)
		root = ET.fromstring(text)
		writer = ET.ElementTree(root)
		writer.write(xmlpath)
		
def parse_raw_data_to_json():
	newsglob = os.path.join(DATA_FOLDER, "*.xml")
	newsfiles = glob.glob(newsglob)
	jsonresult = []
	for newsfile in newsfiles:
		pricecsv = newsfile[:-3] + "csv"
		if not os.path.isfile(pricecsv):
			myprint(pricecsv + " does not exist, cannot use " + newsfile + " for training", 5)
			continue
		
		priceinfo = {}
		with open(pricecsv, newline='') as csvfile:
			csvreader = csv.reader(csvfile, delimiter=',')
			next(csvreader, None)  # skip the headers
			info = next(csvreader, None)
			if info == None:
				continue
			myprint(info, 0)
			priceinfo["Date"] = info[0]
			priceinfo["Open"] = float(info[1])
			priceinfo["High"] = float(info[2])
			priceinfo["Low"] = float(info[3])
			priceinfo["Close"] = float(info[4])
			priceinfo["Volume"] = float(info[5])
			priceinfo["Adj Close"] = float(info[6])
				
		root = ET.parse(newsfile).getroot()
		newslist = []
		for item in root.iter('item'):
			newsinfo = {}
			for child in item:
				newsinfo[child.tag] = child.text
			newslist.append(newsinfo)
		
		priceinfo["news"] = newslist
		priceinfo["source"] = newsfile
		jsonresult.append(priceinfo)
		
	with open(PROCESS_DATA, 'w') as jsonfile:
		jsonstr = json.dumps(jsonresult, sort_keys=True,
		indent=4, separators=(',', ': '))
		jsonfile.write(jsonstr)
		
def jsondata_to_sentiment():
	with open(PROCESS_DATA, 'r') as jsonfile:
		featurejson = json.load(jsonfile)
		
	sid = SentimentIntensityAnalyzer()
	total = 0
	good = 0
	bad = 0
	guessedright = 0
	for data in featurejson:
		newslist = data["news"]
		sums = {"compound":0, "neg":0, "neu":0, "pos":0}
		for news in newslist:
			title = news["title"]
			ss = sid.polarity_scores(title)
			#print(title)
			for k in sorted(ss):
				#print('{0}: {1}, '.format(k, ss[k]), end='')
				sums[k] += ss[k]
		for key in sums:
			sums[key] /= len(newslist)
			
		print(data["source"])
		for k in sorted(sums):
			print('{0}: {1}, '.format(k, sums[k]), end='')
			print(" gain : ", data["Close"] - data["Open"])
		print()
		
def download_news_pages():
	with open(PROCESS_DATA, 'r') as jsonfile:
		featurejson = json.load(jsonfile)
		
	totalnews = 0
	totaldays = 0
	for data in featurejson:
		newslist = data["news"]
		source = data["source"] # xml the data came from
		index = 0
		totaldays += 1
		for news in newslist:
			totalnews += 1
			url = news["link"]
			htmlpath = source + str(index) + ".html"
			index += 1
			if "contents" not in news and os.path.isfile(htmlpath):
				myprint("Added missing path " + htmlpath, 2)
				news["contents"] = htmlpath
			if os.path.isfile(htmlpath):
				myprint(htmlpath + " already exists", 1)
				continue
				
			myprint("follow news link " + url,1)
			text = downloadURL(url)
			with open(htmlpath, 'wb') as htmlfile:
				htmlfile.write(text.encode('utf-8'))
			news["contents"] = htmlpath
			
	with open(PROCESS_DATA, 'w') as jsonfile:
		jsonstr = json.dumps(featurejson, sort_keys=True,
		indent=4, separators=(',', ': '))
		jsonfile.write(jsonstr)
			
	myprint("Parsed " + str(totalnews) + " news for " + str(totaldays) + " symbols/day", 2)
	if totaldays != 0:
		myprint("Average news per symbol : " + str(totalnews/totaldays), 2)
	
from languageprocessing import *

def process_news(news, stopwords, filename):
	word_dict = extract_words(news)
	remove_stopwords(word_dict, stopwords)
	save_word_dict(word_dict, filename + ".words")

def process_all_news():
	stop_words = load_stopwords('./stopwords.txt')
	
	with open(PROCESS_DATA, 'r') as jsonfile:
		featurejson = json.load(jsonfile)
		
	for data in featurejson:
		newslist = data["news"]
		for news in newslist:
			title = news["title"]
			content = ""
			if "contents" in news and news["contents"] is not None:
				content = news["contents"]
			process_news(title, stop_words, content)
	
def generate_word_counts():
	wordglob = os.path.join(DATA_FOLDER, "*.words")
	wordfiles = glob.glob(wordglob)
	return count_all_words(wordfiles)
	
def sort_dict(v, asc=True):
	if asc:
		sorted_dict = sorted(v.items(), key=operator.itemgetter(1))
		return sorted_dict
	else:
		pass
		


if __name__ == '__main__':
	#nltk.download()
	#update_news()
	#update_52_prices()
	#pricecsv_to_json()
	#update_prices()
	#parse_raw_data_to_json()
	#download_news_pages()
	#jsondata_to_sentiment()
	#process_all_news()
	ret = generate_word_counts()
	myprint(sort_dict(ret), 1)
	
	myprint("done", 5)