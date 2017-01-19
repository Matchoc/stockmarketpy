import json
import sys
import os

if __name__ == '__main__':
	news_link_path = os.path.join("data", "news_link.json")
	with open(news_link_path, 'r') as jsonfile:
		tickers = json.load(jsonfile)
		
	print(len(tickers))
		
	sys.exit()
		
	new_tickers = [
		"AAR.UN",
		"AAV",
		"ABX",
		"AC",
		"ACO-X",
		"AD",
		"AEM",
		"AGI",
		"AGU",
		"AIF",
		"AIM",
		"AKG",
		"ALA",
		"AP-UN",
		"AQN",
		"ARE",
		"ARX",
		"ASR",
		"ATA",
		"ATD-B",
		"AX-UN",
		"AYA",
		"BAD",
		"BAM.A",
		"BB",
		"BBD-B",
		"BBU-UN",
		"BCB",
		"BCE",
		"BEI-UN",
		"BEP.UN",
		"BIR",
		"BMO",
		"BNE",
		"BNP",
		"BNS",
		"BPY.UN",
		"BTE",
		"BTO",
		"BYD.UN",
		"CAE",
		"CAR.UN",
		"CCA",
		"CCL.B",
		"CCO",
		"CEU",
		"CFP",
		"CG",
		"CGX",
		"CHE.UN",
		"CIGI",
		"CIX",
		"CJR.B",
		"CLS",
		"CM",
		"CMG",
		"CNQ",
		"CNR",
		"CP",
		"CPG",
		"CPX",
		"CR",
		"CRR.UN",
		"CSH.UN",
		"CSU",
		"CTC.A",
		"CU",
		"CUF.UN",
		"CVE",
		"CWB",
		"D.UN",
		"DDC",
		"DGC",
		"DH",
		"DHX.B",
		"DII.B",
		"DOL",
		"DOO",
		"DRG.UN",
		"DSG",
		"ECA",
		"ECI",
		"ECN",
		"EDV",
		"EFN",
		"EFX",
		"EIF",
		"ELD",
		"EMA",
		"EMP.A",
		"ENB",
		"ENF",
		"ENGH",
		"ERF",
		"ESI",
		"EXE",
		"FCR",
		"FFH",
		"FM",
		"FNV",
		"FR",
		"FRU",
		"FSV",
		"FTS",
		"FTT",
		"FVI",
		"G",
		"GC",
		"GEI",
		"GIB.A",
		"GIL",
		"GRT.UN",
		"GTE",
		"GUD",
		"GUY",
		"GWO",
		"H",
		"HBC",
		"HBM",
		"HCG",
		"HR.UN",
		"HSE",
		"IAG",
		"IFC",
		"IFP",
		"IGM",
		"IMG",
		"IMO",
		"INE",
		"IPL",
		"IT",
		"ITP",
		"IVN",
		"JE",
		"K",
		"KDX",
		"KEL",
		"KEY",
		"KL",
		"KXS",
		"L",
		"LB",
		"LIF",
		"LNR",
		"LUC",
		"LUN",
		"MAG",
		"MBT",
		"MDA",
		"MEG",
		"MFC",
		"MFI",
		"MG",
		"MIC",
		"MNW",
		"MRE",
		"MRU",
		"MSI",
		"MST.UN",
		"MTL",
		"MX",
		"NA",
		"NFI",
		"NG",
		"NGD",
		"NPI",
		"NSU",
		"NVA",
		"NVU.UN",
		"NWC",
		"OGC",
		"ONEX",
		"OR",
		"OSB",
		"OTC",
		"PAA",
		"PBH",
		"PD",
		"PEY",
		"PJC.A",
		"PKI",
		"PLI",
		"POT",
		"POW",
		"PPL",
		"PSI",
		"PSK",
		"PVG",
		"PWF",
		"PXT",
		"QBR.B",
		"QSR",
		"RBA",
		"RCI.B",
		"REF.UN",
		"REI.UN",
		"RNW",
		"RRX",
		"RUS",
		"RY",
		"SAP",
		"SCL",
		"SES",
		"SGY",
		"SJ",
		"SJR.B",
		"SLF",
		"SLW",
		"SMF",
		"SNC",
		"SPB",
		"SPE",
		"SRU.UN",
		"SSL",
		"SSO",
		"STN",
		"SU",
		"SW",
		"T",
		"TA",
		"TCL.A",
		"TCN",
		"TD",
		"TECK.B",
		"TFII",
		"THO",
		"TIH",
		"TOG",
		"TOU",
		"TRI",
		"TRP",
		"TRQ",
		"TXG",
		"UNS",
		"VET",
		"VII",
		"VRX",
		"VSN",
		"WCN",
		"WCP",
		"WEF",
		"WFT",
		"WJA",
		"WN",
		"WPK",
		"WSP",
		"WTE",
		"X",
		"YRI",
		"ZZZ"
	]
	
	news_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={}.to&region=US&lang=en-US"
	prices_url = "http://real-chart.finance.yahoo.com/table.csv?s={}.TO&ignore=.csv"
	
	added = 0
	for new_ticker in new_tickers:
		new_ticker = new_ticker.replace(".", "-") #yahoo uses - as separator and . for the exchange name
		if new_ticker not in tickers:
			added += 1
			data = {}
			data["news"] = news_url.format(new_ticker)
			data["prices"] = prices_url.format(new_ticker)
			tickers[new_ticker] = data
			
	with open(news_link_path, 'w') as fo:
		json.dump(tickers, fo, sort_keys=True,
		indent=4, separators=(',', ': '))
		
	print("Added " + str(added))
	print("Done")