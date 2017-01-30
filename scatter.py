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
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import label_ranking_average_precision_score

#https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20in%20(%22YHOO%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback=
#http://download.finance.yahoo.com/d/quotes.csv?s=AAPL&f=nl1r&e=.csv
#a Ask
#a2 Average Daily Volume
#a5 Ask Size
#b Bid
#b2 Ask (Real-time)
#b3 Bid (Real-time)
#b4 Book Value
#b6 Bid Size
#c Change & Perscent Change
#c1 Change
#c3 Commission
#c4 Currency
#c6 Change (Real-Time)
#c8 Afeter Hours Change (Real-Time)
#d Dividend/Share
#d1 Last Trade Date
#d2 Trade Date
#e Earnings/Share
#e1 Error Indication (returned for symbol changed / invalid)
#e7 EPS Estimate Current Year
#e8 EPS Estimate Next Year
#e9 EPS Estimate Next Quarter
#f0 Trade Links Additional
#f6 Float Shares
#g Day's Low
#g1 Holdings Gain Percent
#g3 Annualized Gain
#g4 Holdings Gain
#g5 Holdings Gain Percent (Real-Time)
#g6 Holdings Gain (Real-Time)
#h Day's High
#i 	More Info
#i5 	Order Book (Real-time)
#j 	52-week Low
#j1 	Market Capitalization
#j2 	Shares Outstanding
#j3 	Market Cap (Real-time)
#j4 	EBITDA
#j5 	Change From 52-week Low
#j6 	Percent Change From 52-week Low
#k 	52-week High
#k1 	Last Trade (Real-time) With Time
#k2 	Change Percent (Real-time)
#k3 	Last Trade Size
#k4 	Change From 52-week High
#k5 	Percent Change From 52-week High
#l 	Last Trade (With Time)
#l1 	Last Trade (Price Only)
#l2 	High Limit
#l3 	Low Limit
#m 	Day’s Range
#m2 	Day’s Range (Real-time)
#m3 	50-day Moving Average
#m4 	200-day Moving Average
#m5 	Change From 200-day Moving Average
#m6 	Percent Change From 200-day Moving Average
#m7 	Change From 50-day Moving Average
#m8 	Percent Change From 50-day Moving Average
#n 	Name
#n4 	Notes
#o 	Open
#p 	Previous Close
#p1 	Price Paid
#p2 	Change in Percent
#p5 	Price/Sales
#p6 	Price/Book
#q 	Ex-Dividend Date
#r 	P/E Ratio
#r1 	Dividend Pay Date
#r2 	P/E Ratio (Real-time)
#r5 	PEG Ratio
#r6 	Price/EPS Estimate Current Year
#r7 	Price/EPS Estimate Next Year
#s 	Symbol
#s1 	Shares Owned
#s6 	Revenue
#s7 	Short Ratio
#t1 	Last Trade Time
#t6 	Trade Links
#t7 	Ticker Trend
#t8 	1 yr Target Price
#v 	Volume
#v1 	Holdings Value
#v7 	Holdings Value (Real-time)
#w 	52-week Range
#w1 	Day’s Value Change
#w4 	Day’s Value Change (Real-time)
#x 	Stock Exchange
#y 	Dividend Yield

YAHOO_URL = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20in%20(%22{}%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback="

PRINT_LEVEL=1
def myprint(msg, level=0):
	if (level >= PRINT_LEVEL):
		sys.stdout.buffer.write((str(msg) + "\n").encode('UTF-8'))

		
def sort_dict(v, asc=True):
	if asc:
		sorted_dict = sorted(v.items(), key=operator.itemgetter(1))
		return sorted_dict
	else:
		pass
		
def calc_moving_avg(data, timerange):
	pass
		
def calc_sharpe_ratio(data, timerange):
	pass
	
def calc_alpha_beta(data, timerange):
	pass
	
def get_basic_data(symbol, data):
	pass

def run_symbol(steps, symbol, data):
	pass
	
def get_yahoo_data(symbols):
	agregate_symbol = [symbol + ".to" for symbol in symbols]
	num_symbol = len(agregate_symbol)
	step = 50
	results = []
	for i in range(0, num_symbol, step):
		formated_url = YAHOO_URL.format(",".join(agregate_symbol[i:i + step]))
		text = downloadURL(formated_url)
		jsontext = json.loads(text)
		results.append(jsontext)
		
	final_result = {}
	for result in results:
		quote_list = result["query"]["results"]["quote"]
		for quote in quote_list:
			symbol = quote["symbol"]
			final_result[symbol] = quote
			
	return final_result
	
	
def save_technicals(technicals):
	filename = get_combined_technicals_json()
	with open(filename, 'w') as fo:
		json.dump(technicals, fo, sort_keys=True,
		indent=4, separators=(',', ': '))
	timestr = strftime("%Y%m%d-%H%M%S")
	historical_filename = timestr + "-" + filename
	with open(historical_filename, 'w') as fo:
		json.dump(technicals, fo, sort_keys=True,
		indent=4, separators=(',', ': '))
		
def get_tech_xy(data, technicals = None):
	if technicals is None:
		technicals = load_technicals_json()
		
	name_list = data["name_list"]
	daterange = data["daterange"]
		
	nowdate = datetime.datetime.now()
	earlydate = nowdate - daterange
		
	x = []
	y = []
	for symbol in technicals:
		data = []
		raw_symbol = symbol.replace(".to", "")
		prices = get_price_json(raw_symbol)
		
		iter_date = nowdate
		nowprice = None
		earlyprice = None
		while iter_date >= earlydate:
			pricedatefmt = iter_date.strftime("%Y-%m-%d")
			if pricedatefmt in prices:
				earlyprice = prices[pricedatefmt]["Adj Close"]
				if nowprice is None:
					nowprice = earlyprice
			iter_date -= datetime.timedelta(days=1)
			
		if nowprice is None or earlyprice is None:
			myprint("[" + symbol + "] ERROR: could not find valid start or end price between : " + str(nowdate) + " and " + str(earlydate), 5)
			nowprice = 1
			earlyprice = 1
			
		per_return = nowprice / earlyprice - 1.0
		
		for name in name_list:
			#print("technical[" + symbol + "][" + name + "] = " + str(technicals[symbol][name]))
			val = parse_shortened_price(technicals[symbol][name])
			if val is None:
				val = 0
			data.append(val)
		x.append(data)
		y.append(per_return)
		
	return x, y

def save_regression_machine(machine, scaler):
	machine_filepath = get_regression_machine_path()
	scaler_filepath = get_regression_scaler_path()
	joblib.dump(machine, machine_filepath)
	joblib.dump(scaler, scaler_filepath)
	
def load_regression_machine():
	machine_filepath = get_regression_machine_path()
	scaler_filepath = get_regression_scaler_path()
	machine = joblib.load(machine_filepath)
	scaler = joblib.load(scaler_filepath)
	return machine, scaler
	
def train_regression(data, technicals = None):
	x, y = get_tech_xy(data, technicals)
	
	regressor = LinearRegression(fit_intercept=True, normalize=False, copy_X=True, n_jobs=1)
	reg_scaler = StandardScaler()
	reg_scaler.fit(x)
	x = reg_scaler.transform(x)
	regressor.fit(x, y)
	
	save_regression_machine(regressor, reg_scaler)
	
	myprint("trainined regressor with " + str(len(x)) + " values", 3)
	myprint("Regressor Intercept : " + str(regressor.intercept_), 3)
	myprint("COEFs :", 3)
	count = 0
	for i in data["name_list"]:
		myprint(i + " : " + str(regressor.coef_[count]), 3)
		count += 1
	
	
def run_all_symbols(steps = ["dltechnicals", "plot"], extradata = None):
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		links = json.load(jsonfile)
	
	count = 0
	data = {}
	technicals = None
		
	if "dltechnicals" in steps:
		technicals = get_yahoo_data(list(links.keys()))
		save_technicals(technicals)
		
	if "plot" in steps:
		if "daterange" in extradata:
			daterange = extradata["daterange"]
		if "plotname" in extradata:
			plotname = extradata["plotname"]
		generate_plot(plotname, daterange, technicals)
		
	if "regression" in steps:
		train_regression(extradata, technicals)
	
	
	#for symbol in links:
	#	count += 1
	#	data[symbol] = {}
	#	myprint("Processing symbol " + symbol + " (" + str(count) + "/" + str(len(links)) + ")", 2)
	#	run_symbol(steps, symbol, data)
		
	return data
	
def is_float(pricestr):
	if pricestr is None:
		return False
	try:
		val = float(pricestr)
		return True
	except ValueError:
		return False
		
def parse_shortened_price(pricestr):
	if pricestr is None:
		return None
	
	if is_float(pricestr):
		return float(pricestr)
		
	if "B" in pricestr:
		part = pricestr.replace("B", "")
		if is_float(part):
			return float(part) * 1000000000
		else:
			return None
	
	if "M" in pricestr:
		part = pricestr.replace("M", "")
		if is_float(part):
			return float(part) * 1000000
		else:
			return None
			
	if "%" in pricestr:
		return float(pricestr.replace("%", ""))
		
	return None
	
def get_mean(name, techs = None):
	if techs is None:
		techs = load_technicals_json()
		
	count = 0
	tech_avg = 0
	for symbol in techs:
		if techs[symbol][name] is None:
			continue
			
		val = parse_shortened_price(techs[symbol][name])
		tech_avg += val
		count += 1
	
	return tech_avg / count
	
def get_std_dev(name, techs = None):
	if techs is None:
		techs = load_technicals_json()
		
	tech_mean = get_mean(name, techs)
	sum_diff = 0
	count = 0
	for symbol in techs:
		if techs[symbol][name] is None:
			continue
		
		val = parse_shortened_price(techs[symbol][name])
		sum_diff += (val - tech_mean) ** 2
		count += 1
		
	std_diff = (sum_diff / count) ** 0.5
	
	return std_diff
	
def generate_plot(yname, daterange, techs = None):
	if techs == None:
		techs = load_technicals_json()
		
	nowdate = datetime.datetime.now()
	earlydate = nowdate - daterange
	std_dev = get_std_dev(yname, techs)
	tech_mean = get_mean(yname, techs)
	
	x = []
	y = []
	for symbol in techs:
		if techs[symbol][yname] is None:
			continue
			
		raw_symbol = symbol.replace(".to", "")
		prices = get_price_json(raw_symbol)
		nowprice = None
		earlyprice = None
		iter_date = nowdate
		while iter_date >= earlydate:
			pricedatefmt = iter_date.strftime("%Y-%m-%d")
			if pricedatefmt in prices:
				earlyprice = prices[pricedatefmt]["Adj Close"]
				if nowprice is None:
					nowprice = earlyprice
			iter_date -= datetime.timedelta(days=1)
			
		if nowprice is None or earlyprice is None:
			myprint("[" + symbol + "] ERROR: could not find valid start or end price between : " + str(nowdate) + " and " + str(earlydate), 5)
			nowprice = 1
			earlyprice = 1
	
		per_return = nowprice / earlyprice - 1.0
		myprint("[" + symbol + "] " + yname, 2)
		yval = parse_shortened_price(techs[symbol][yname])
		if yval is not None and (abs(yval) - tech_mean) <= std_dev:
			y.append(yval)
			x.append(per_return)
		else:
			myprint("[" + symbol + "] ERROR: failed to parse " + yname + " into float : " + str(techs[symbol][yname]), 5)
		
	plt.plot(y, x, 'ro', label=yname)
	plt.legend()
	plt.show()
		
	
def data_available_for_all():
	technicalspath = get_combined_technicals_json()
	with open(technicalspath, 'r') as jsonfile:
		technicals = json.load(jsonfile)
		
	alldata = {}
	for symbol in technicals:
		for data in technicals[symbol]:
			if technicals[symbol][data] is not None and data not in alldata:
				alldata[data] = 1
	
	as_string = json.dumps(alldata, sort_keys=True,
		indent=4, separators=(',', ': '))
		
	myprint(as_string, 5)
	
if __name__ == '__main__':
	desired_features = [
		"AverageDailyVolume",
		"BookValue",
		"DividendShare",
		"DividendYield",
		"EBITDA",
		"EPSEstimateCurrentYear",
		"EPSEstimateNextQuarter",
		"EarningsShare",
		"FiftydayMovingAverage",
		"MarketCapitalization",
		"PEGRatio",
		"PERatio",
		"PriceBook",
		"PriceEPSEstimateCurrentYear",
		"PriceEPSEstimateNextYear",
		"PriceSales",
		"ShortRatio",
		"TwoHundreddayMovingAverage"
	]
	run_all_symbols([
			#"plot",
			"regression",
			"none" # put this here so I don't have to add , when I change list size.
		], 
		{
			"plotname": "ShortRatio", 
			"daterange": datetime.timedelta(weeks=52),
			"name_list": desired_features
		})
	#data_available_for_all()
	
	myprint("done", 5)