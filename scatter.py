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
	
def run_all_symbols(steps):
	with open(RSS_FEED_FILENAME, 'r') as jsonfile:
		links = json.load(jsonfile)
	
	count = 0
	data = {}
	for symbol in links:
		count += 1
		data[symbol] = {}
		myprint("Processing symbol " + symbol + " (" + str(count) + "/" + str(len(links)) + ")", 2)
		run_symbol(steps, symbol, data)
		
	return data
		
	
if __name__ == '__main__':
	run_all_symbols([])
	
	myprint("done", 5)