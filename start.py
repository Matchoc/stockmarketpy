import urllib.request
import urllib.error
import sys
from stockmarket import *

if __name__ == '__main__':
	set_skip_symbol("")
	update_all_symbols(["dlprice", "dlrss", "price2json", "rss2json", "dlnews", "processnews", "today", "updateCSV"])
	