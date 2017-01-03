import urllib.request
import urllib.error
import sys

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
		myprint("HEADER : " + str(e.headers), 1)
		return ""
	except UnicodeDecodeError as e:
		myprint("URL failed : Response not unicode", 5)
		return ""
	return text

if __name__ == '__main__':
	
	#url = "http://us.rd.yahoo.com/finance/external/noodlsaunz/rss/SIG=128vmbevt/*http://www.publicnow.com/view/E91D6AF150102C9807B2BEC95303A5AF8B07FFBB"
	#url = "http://www.publicnow.com/view/E91D6AF150102C9807B2BEC95303A5AF8B07FFBB"
	#url = "http://us.rd.yahoo.com/finance/external/noodlsaunz/rss/SIG=128sqfhpf/*http://www.publicnow.com/view/E1D28FD954712D35E493604B4084802ED959120B"
	url = "http://us.rd.yahoo.com/finance/external/noodlsaunz/rss/SIG=128qmscvv/*http://www.publicnow.com/view/0E2EA80E075F31A37B2F862C566EF1E0D5BB3CE5"
	text = downloadURL(url)
	print(text)
	