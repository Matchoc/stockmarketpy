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
	#train_cross_variations()
	#graph_actual_vs_predicted()
	#update_symbol("BNS")
	
	# Update everything (word list, training, news, all the bang)
	#update_all_symbols(["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "allwords", "updateTraining", "train"])
	
	# Update news and do a prediction based only on previous training and word list (don't update word list or machine)
	#update_all_symbols(["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "today"])
	#update_all_symbols(["train", "today"])
	
	# Update everything and do a cross-validation check (will printout a square mean variation)
	#update_all_symbols(["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "allwords", "updateTraining", "train", "crossval"])
	
	#update_all_symbols(["processnews", "allwords", "updateTraining", "train"])
	#update_all_symbols(["train"])
	#update_all_symbols(["price2json", "rss2json"])
	#update_all_symbols(["dlnews", "processnews"])
	#update_all_symbols(["processnews", "allwords"])
	#update_all_symbols(["allwords"])
	#update_all_symbols(["train"])
	#update_all_symbols(["train"])
	#update_all_symbols(["train", "crossval"])
	#update_all_symbols(["crossval"])
	#update_all_symbols(["today", "updateCSV"])
	update_all_symbols(["dlprice", "price2json", "updateCSV"])
	
	myprint("done", 5)