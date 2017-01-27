import sys
import os
import json
import datetime
import csv
import urllib.request
import urllib.error
import http.client
import xml.etree.ElementTree as ET
from time import strftime
from bs4 import BeautifulSoup

DATA_FOLDER = "data"
RSS_FEED_FILENAME = os.path.join(DATA_FOLDER, "news_link.json")

def get_training_json(symbol):
	return os.path.join(DATA_FOLDER, symbol, "training.json")

def get_price_json(symbol):
	csvpath = get_price_csv_path(symbol)
	jsonpath = csvpath.replace(".csv", ".json")
	with open(jsonpath, 'r') as jsonfile:
		prices = json.load(jsonfile)
	return prices

def get_price_csv_path(symbol):
	return os.path.join(DATA_FOLDER, symbol, "prices.csv")

def get_price_url(symbol):
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		links = json.load(jsonfile)
	url = links[symbol]["prices"]
	return url
	
def get_yahoo_rss_url(symbol):
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		links = json.load(jsonfile)
	url = links[symbol]["news"]
	return url

def get_news_json_path(symbol):
	return os.path.join(DATA_FOLDER, symbol, "news.json")

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
		text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
	except http.client.IncompleteRead as e:
		data = e.partial
		text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
	except urllib.error.HTTPError as e:
		myprint("URL failed : " + str(e.code) + " " + e.reason, 5)
		return ""
	except UnicodeDecodeError as e:
		myprint("URL failed : Response not unicode", 5)
		return ""
	return text

def download_year_prices(symbol):
	#end, start
	#month, day, year, month, day, year
	#11 3 2016 0 12 1995 
	#&d=11&e=3&f=2016&g=d&a=0&b=12&c=1995
	url = get_price_url(symbol)
	
	today = datetime.date.today()# - datetime.timedelta(days=1)
	month = today.month
	year = today.year
	day = today.day
	dateparam = "&d={}&e={}&f={}&g=d&a={}&b={}&c={}".format(month-1, day, year, month-1, day, year-1)
	
	url += dateparam
	myprint("get price : " + url,1)
	text = downloadURL(url)
	if text == None:
		myprint("Price list empty", 5)
		
	#timestr = "-{year}{month:02d}{day:02d}".format(year=year, month=month, day=day)
	csvpath = get_price_csv_path(symbol)
	myprint(text[0:180], 1)
	with open(csvpath, 'w') as csvfile:
		csvfile.write(text)
		
	return csvpath

def download_yahoo_rss(symbol):
	url = get_yahoo_rss_url(symbol)
	myprint("get news : " + url,1)
	
	today = datetime.date.today()# - datetime.timedelta(days=1)
	month = today.month
	year = today.year
	day = today.day
	timestr = "{year}{month:02d}{day:02d}".format(year=year, month=month, day=day)
	xmlpath = os.path.join(DATA_FOLDER, symbol, timestr + ".rss")
	
	text = downloadURL(url)
	root = ET.fromstring(text)
	writer = ET.ElementTree(root)
	writer.write(xmlpath)
	return xmlpath
	
def convert_prices_to_json(symbol):
	csvpath = get_price_csv_path(symbol)
	priceinfo = {}
	with open(csvpath, newline='') as csvfile:
		csvreader = csv.reader(csvfile, delimiter=',')
		info = next(csvreader, None)  # skip the headers
		while info is not None:
			info = next(csvreader, None)
			if info == None:
				break
			priceinfo[info[0]] = {}
			priceinfo[info[0]]["Open"] = float(info[1])
			priceinfo[info[0]]["High"] = float(info[2])
			priceinfo[info[0]]["Low"] = float(info[3])
			priceinfo[info[0]]["Close"] = float(info[4])
			priceinfo[info[0]]["Volume"] = float(info[5])
			priceinfo[info[0]]["Adj Close"] = float(info[6])

	with open(csvpath.replace(".csv", ".json"), 'w') as fo:
		json.dump(priceinfo, fo, sort_keys=True,
		indent=4, separators=(',', ': '))
	
	return csvpath
		
def convert_yahoorss_to_json(symbol, newsxmlpath):
	newsjsonpath = get_news_json_path(symbol)
	
	root = ET.parse(newsxmlpath).getroot()
	newslist = []
	for item in root.iter('item'):
		newsinfo = {}
		for child in item:
			newsinfo[child.tag] = child.text
		newsinfo["source"] = newsxmlpath
		newslist.append(newsinfo)
	
	if os.path.isfile(newsjsonpath):
		with open(newsjsonpath, 'r') as jsonfile:
			previousnews = json.load(jsonfile)
	else:
		previousnews = []
	
	#remove duplicates (same link == 100% sure same news)
	for news in previousnews:
		url = news["link"]
		for newnews in newslist:
			newurl = newnews["link"]
			if newurl == url:
				newslist.remove(newnews)
				
	previousnews += newslist
	with open(newsjsonpath, 'w') as fo:
		json.dump(previousnews, fo, sort_keys=True,
		indent=4, separators=(',', ': '))
		
	return newsjsonpath

def download_all_news_page(symbol):
	newsjsonpath = get_news_json_path(symbol)
	with open(newsjsonpath, 'r') as jsonfile:
		allnews = json.load(jsonfile)
	for news in allnews:
		if "contents" in news and os.path.isfile(news["contents"]):
			myprint("contents already downloaded, skipped : " + news["contents"], 1)
			continue
		dlpath = download_news_page(symbol, news["link"])
		news["contents"] = dlpath
	
	with open(newsjsonpath, 'w') as fo:
		json.dump(allnews, fo, sort_keys=True,
		indent=4, separators=(',', ': '))
	
def download_news_page(symbol, newsurl):
	timestr = strftime("%Y%m%d-%H%M%S")
	htmlpath = os.path.join(DATA_FOLDER, symbol, timestr + ".news")
	myprint("follow news link " + newsurl,1)
	text = downloadURL(newsurl)
	with open(htmlpath, 'wb') as htmlfile:
		htmlfile.write(text.encode('utf-8'))
	return htmlpath
	
def get_important_text_from_news(htmlpath):
	myprint("BeautifulSoup : " + htmlpath, 1)
	with open(htmlpath, 'rb') as f:
		text = f.read()
		soup = BeautifulSoup(text.decode("utf-8", "ignore"), "html.parser", from_encoding="utf-8")
	
	paragraphs = soup.findAll('p')
	words = [p.text for p in paragraphs]
	return "".join(words)

def add_real_price_csv(csvpath):
	filename, filedate, filetime = csvpath.split("-")
	lookupdate = datetime.datetime.strptime(filedate, '%Y%m%d')
	pricedatefmt = lookupdate.strftime("%Y-%m-%d")
	newcsv = []
	myprint("updating CSV " + csvpath, 1)
	
	with open(csvpath, newline='', errors="ignore") as csvfile:
		csvreader = csv.reader(csvfile, delimiter=';')
		info = next(csvreader, None)  # skip the headers
		# 8 column means real price has already been updated.
		if len(info) > 7:
			myprint("CSV already up-to-date", 1)
			return
		if len(info) < 7:
			myprint("CSV is legacy, skipping", 1)
			return
			
		newcsv = [["symbol", "prediction $", "prediction %", "last close", "pubDate", "pubTime", "real $", "real %", "per wrong", "title"]]
		while info is not None:
			info = next(csvreader, None)
			if info == None:
				break
				
			#title.append("symbol")
			#title.append("prediction $")
			#title.append("prediction %")
			#title.append("last close")
			#title.append("pudDate")
			#title.append("pudTime")
			#title.append("title")
		
			symbol = info[0]
			preddol = float(info[1])
			predper = float(info[2])
			predclose = float(info[3])
			preddate = info[4]
			predtime = info[5]
			predtitle = info[6]
			
			prices = get_price_json(symbol)
			if pricedatefmt not in prices:
				myprint("price not found for " + symbol, 1)
				return
				
			adjclosetoday = prices[pricedatefmt]["Adj Close"]
			adjcloseyesterday = get_previous_close_price(lookupdate, prices)
			
			realchange = adjclosetoday - adjcloseyesterday
			realper = realchange / predclose * 100.0
			if realchange == 0:
				realchange = 0.0000001
			perwrong = (realchange - preddol) / realchange
			perwrong = abs(perwrong)
			if (realchange > 0 and preddol < 0) or (realchange < 0 and preddol > 0):
				perwrong = perwrong * -1.0
			
			result = [symbol, str(preddol), str(predper), str(predclose), preddate, predtime, str(realchange), str(realper), str(perwrong), predtitle]
			myprint("updated line " + str(result), 1)
			newcsv.append(result)
			
	with open(csvpath, 'wb') as f:
		for line in newcsv:
			f.write((";".join(line) + "\n").encode("utf-8", "ignore"))			
				
			
def get_previous_close_price(cur_date, prices):
	prev_day = cur_date - datetime.timedelta(days=1)
	end_search = cur_date - datetime.timedelta(days=365)
	pricedatefmt = prev_day.strftime("%Y-%m-%d")
	while pricedatefmt not in prices and prev_day > end_search:
		prev_day = prev_day - datetime.timedelta(days=1)
		pricedatefmt = prev_day.strftime("%Y-%m-%d")
	
	if pricedatefmt not in prices:
		# Should error ?
		return 0
	
	return prices[pricedatefmt]["Adj Close"]
	
def get_info_from_yahoo(symbol):
	pass