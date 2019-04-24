#!/usr/bin/python

import os
import subprocess
import sys
import time
import datetime
import argparse
import re
from subprocess import Popen, PIPE
from multiprocessing import Process
from colorama import *

#just setting up a custom help message
helpMessage = """
  scouter.py 10.10.10.10 [output] [interface] [UDP scan options]
  scouter.py 10.10.10.10
  scouter.py 10.10.10.10 -oN -i tun0 -s
  scouter.py 10.10.10.10 -oN --interface tun0 --slow

output:
  -oA: save output in the nmap three major formats at once
  -oN: save output in the nmap normal format
  -oX: save output in the nmap XML format
  -oS: save output in the nmap s|<rIpt kIddi3 format
  -oG: save output in the nmap Grepable format

interface:
  -i, --interface: select an interface for masscan to scan against, default is tun0

UDP scan options:
  -s, --slow: enable slower UDP scan against the top 100 UDP ports, default is no rate limit scan of UDP top 500"""

#doing argument parsing
parser = argparse.ArgumentParser(add_help=False, usage=helpMessage)
parser.add_argument("host", type=str, help="ip address of target")
parser.add_argument("-s", "--slow", help="enable a slower, more accurate UDP scan",
                    action="store_true")
parser.add_argument("-i", "--interface", default="tun0", type=str, nargs="?", help="select which interface to masscan, default is 'tun0'", metavar='interface')
parser.add_argument("-oA", help="save output in the nmap three major formats at once",
                    action="store_true")
parser.add_argument("-oN", help="save output in the nmap normal format",
                    action="store_true")
parser.add_argument("-oX", help="save output in the nmap XML format",
                    action="store_true")
parser.add_argument("-oS", help="save output in the nmap s|<rIpt kIddi3 format",
                    action="store_true")
parser.add_argument("-oG", help="save output in the nmap Grepable format",
                    action="store_true")

args = parser.parse_args()
host = args.host
interface = args.interface

#assigning variable values according to arguments for output
if args.oA:
		output = "-oA"
elif args.oN:
		output = "-oN"
elif args.oX:
		output = "-oX"
elif args.oS:
		output = "-oS"
elif args.oG:
		output = "-oG"
else:
		output = ""

filePath = os.popen("pwd").read()
filePath = filePath.rstrip("\r\n")

if output !="":
	if output == "-oA":
		reportMessage1 = "Outputfile: " + filePath + "/scouter.nmap"
		reportMessage2 = "Outputfile: " + filePath + "/scouter.xml"
		reportMessage3 = "Outputfile: " + filePath + "/scouter.gnmap"
		os.popen('echo "" > scouter.nmap')
		os.popen('echo "" > scouter.xml')
		os.popen('echo "" > scouter.gnmap')
		
	elif (output == "-oN") or (output == "-oX") or (output == "-oS") or (output == "-oG"):
		reportMessageNormal = "Outputfile: " + filePath + "/scouter"
		os.popen('echo "" > scouter')

#setting time for the 'Initializing:' print statement below
currentDT = datetime.datetime.now()
zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "

#this will call masscan and nmap for all non default ports and use the output of the one that finishes first. It will then run a follow up -sC -sV scan on those ports if they're open.
def nmap():
	print(Style.BRIGHT + Fore.CYAN + '[+] ' + Style.RESET_ALL + 'Non-default TCP scan is running...')
	global output
	if output != "":
			output = output + " scouter --append-output"
	try:
		processDefault = Popen(["nmap", "-p 2,5,8,10-12,14-16,18,27-29,31,34-36,38-41,44-48,50-52,54-69,71-78,86,87,91-98,101-105,107,108,112,114-118,120-124,126-134,136-138,140-142,145,147-160,162,164-178,180-198,200-210,213-221,223-253,257,258,260-263,265-279,281-300,302-305,307-310,312-339,341-365,367-388,390-405,408-415,418-424,426,428-442,446-457,459-463,466-480,482-496,498,499,501-511,516-523,525-540,542,546,547,549-553,556-562,564-586,588-592,594-615,618-624,626-630,632-635,637-645,647,649-665,669-682,684-686,688-690,692-699,701-704,706-710,712,713,715-719,721,723-725,727-748,750-764,766-776,778-782,784-786,788-799,802-807,809-842,844-872,874-879,881-887,889-897,899,904-910,913-980,982-986,988,989,991,994,996-998,1003-1006,1008,1012-1020,1101,1103,1109,1115,1116,1118,1120,1125,1127-1129,1133-1136,1139,1140,1142-1144,1146,1150,1153,1155-1162,1167,1168,1170-1173,1176-1182,1184,1188-1191,1193-1197,1200,1202-1212,1214,1215,1219-1232,1235,1237-1243,1245,1246,1249-1258,1260-1270,1273-1276,1278-1286,1288-1295,1297-1299,1302-1308,1312-1321,1323-1327,1329-1333,1335-1351,1353-1416,1418-1432,1435-1442,1444-1454,1456-1460,1462-1493,1495-1499,1502,1504-1520,1522,1523,1525-1532,1534-1555,1557-1579,1581,1582,1584-1593,1595-1599,1601-1640,1642-1657,1659-1665,1667-1686,1689-1699,1701-1716,1722,1724-1754,1756-1760,1762-1781,1784-1800,1802-1804,1806-1811,1813-1838,1841-1861,1865-1874,1876-1899,1901-1913,1915-1934,1936-1946,1948-1970,1973,1975-1983,1985-1997,2011,2012,2014-2019,2023-2029,2031,2032,2036,2037,2039,2044,2050-2064,2066,2067,2069-2098,2101,2102,2104,2108-2110,2112-2118,2120,2122-2125,2127-2134,2136-2143,2145-2159,2162-2169,2171-2178,2180-2189,2192-2195,2197-2199,2201-2221,2223-2250,2252-2259,2261-2287,2289-2300,2302-2322,2324-2365,2367-2380,2384-2392,2395-2398,2400,2402-2491,2493-2499,2501-2521,2523,2524,2526-2556,2558-2600,2603,2606,2609-2637,2639-2700,2703-2709,2711-2716,2719-2724,2726-2799,2801-2808,2810,2812-2868,2870-2874,2876-2908,2911-2919,2921-2966,2969-2997,2999,3002,3004,3008-3010,3012,3014-3016,3018-3029,3032-3051,3053-3070,3072-3076,3078-3127,3129-3167,3169-3210,3212-3220,3222-3259,3262-3267,3270-3282,3284-3299,3302-3305,3307-3321,3326-3332,3334-3350,3352-3366,3368,3373-3388,3391-3403,3405-3475,3477-3492,3494-3516,3518-3526,3528-3545,3547-3550,3552-3579,3581-3658,3660-3688,3691-3702,3704-3736,3738-3765,3767-3783,3785-3799,3802-3808,3810-3813,3815-3825,3829-3850,3852-3868,3870,3872-3877,3879,3881-3888,3890-3904,3906-3913,3915-3917,3919,3921-3944,3946-3970,3972-3985,3987-3994,3996,3997,3999,4007-4044,4046-4110,4112-4124,4127,4128,4130-4223,4225-4241,4243-4278,4280-4320,4322-4342,4344-4442,4447,4448,4450-4549,4551-4566,4568-4661,4663-4847,4849-4898,4901-4997,4999,5005-5008,5010-5029,5031,5032,5034-5049,5052,5053,5055-5059,5062-5079,5081-5086,5088-5099,5103-5119,5121-5189,5191-5199,5201-5213,5215-5220,5223,5224,5227-5268,5270-5279,5281-5297,5299-5356,5358-5404,5406-5413,5415-5430,5433-5439,5441-5499,5501-5509,5511-5543,5545-5549,5551-5554,5556-5559,5561-5565,5567-5630,5632,5634-5665,5667-5677,5680-5717,5719-5729,5731-5799,5803-5809,5812-5814,5816-5821,5823,5824,5826-5849,5851-5858,5860,5861,5863-5876,5878-5899,5905,5908,5909,5912-5914,5916-5921,5923,5924,5926-5949,5951,5953-5958,5964-5986,5990-5997,6008,6010-6024,6026-6058,6060-6099,6102-6105,6107-6111,6113-6122,6124-6128,6130-6155,6157-6345,6347-6388,6390-6501,6503-6509,6511-6542,6544-6546,6548-6564,6568-6579,6581-6645,6647-6665,6670-6688,6690,6691,6693-6698,6700-6778,6780-6787,6790,6791,6793-6838,6840-6880,6882-6900,6902-6968,6970-6999,7003,7005,7006,7008-7018,7020-7024,7026-7069,7071-7099,7101,7102,7104,7105,7107-7199,7202-7401,7403-7434,7436-7442,7444-7495,7497-7511,7513-7624,7626,7628-7675,7677-7740,7742-7776,7779-7799,7801-7910,7912-7919,7922-7936,7939-7998,8003-8006,8012-8020,8023-8030,8032-8041,8043,8044,8046-8079,8091,8092,8094-8098,8101-8179,8182-8191,8195-8199,8201-8221,8223-8253,8255-8289,8293-8299,8301-8332,8334-8382,8384-8399,8401,8403-8442,8444-8499,8501-8599,8601-8648,8650,8653,8655-8700,8702-8799,8801-8872,8874-8887,8889-8898,8900-8993,8995-8999,9004-9008,9012-9039,9041-9049,9051-9070,9072-9079,9082-9089,9092-9098,9104-9109,9112-9199,9201-9206,9208-9219,9221-9289,9291-9414,9416,9417,9419-9484,9486-9499,9501,9504-9534,9536-9574,9576-9592,9596-9617,9619-9665,9667-9875,9879-9897,9899,9901-9916,9918-9928,9930-9942,9945-9967,9969-9997,10005-10008,10011,10013-10023,10026-10081,10083-10179,10181-10214,10216-10242,10244-10565,10567-10615,10618-10620,10622-10625,10627,10630-10777,10779-11109,11112-11966,11968-11999,12001-12173,12175-12264,12266-12344,12346-13455,13457-13721,13723-13781,13784-13999,14001-14237,14239-14440,14443-14999,15001,15005-15659,15661-15741,15743-15999,16002-16011,16013-16015,16017,16019-16079,16081-16112,16114-16991,16994-17876,17878-17987,17989-18039,18041-18100,18102-18987,18989-19100,19102-19282,19284-19314,19316-19349,19351-19779,19781-19800,19802-19841,19843-19999,20001-20004,20006-20030,20032-20220,20223-20827,20829-21570,21572-22938,22940-23501,23503-24443,24445-24799,24801-25733,25736-26213,26215-26999,27001-27351,27354,27357-27714,27716-28200,28202-29999,30001-30717,30719-30950,30952-31037,31039-31336,31338-32767,32786-33353,33355-33898,33900-34570,34574-35499,35501-38291,38293-40192,40194-40910,40912-41510,41512-42509,42511-44175,44177-44441,44444-44500,44502-45099,45101-48079,48081-49151,49162,49164,49166,49168-49174,49177-49399,49401-49998,50004,50005,50007-50299,50301-50388,50390-50499,50501-50635,50637-50799,50801-51102,51104-51492,51494-52672,52674-52821,52823-52847,52849-52868,52870-54044,54046-54327,54329-55054,55057-55554,55556-55599,55601-56736,56739-57293,57295-57796,57798-58079,58081-60019,60021-60442,60444-61531,61533-61899,61901-62077,62079-63330,63332-64622,64624-64679,64681-64999,65001-65128,65130-65388,65390-65535", host], stdout=PIPE, stderr=PIPE)
		processAll = Popen(["masscan", "-p2,5,8,10-12,14-16,18,27-29,31,34-36,38-41,44-48,50-52,54-69,71-78,86,87,91-98,101-105,107,108,112,114-118,120-124,126-134,136-138,140-142,145,147-160,162,164-178,180-198,200-210,213-221,223-253,257,258,260-263,265-279,281-300,302-305,307-310,312-339,341-365,367-388,390-405,408-415,418-424,426,428-442,446-457,459-463,466-480,482-496,498,499,501-511,516-523,525-540,542,546,547,549-553,556-562,564-586,588-592,594-615,618-624,626-630,632-635,637-645,647,649-665,669-682,684-686,688-690,692-699,701-704,706-710,712,713,715-719,721,723-725,727-748,750-764,766-776,778-782,784-786,788-799,802-807,809-842,844-872,874-879,881-887,889-897,899,904-910,913-980,982-986,988,989,991,994,996-998,1003-1006,1008,1012-1020,1101,1103,1109,1115,1116,1118,1120,1125,1127-1129,1133-1136,1139,1140,1142-1144,1146,1150,1153,1155-1162,1167,1168,1170-1173,1176-1182,1184,1188-1191,1193-1197,1200,1202-1212,1214,1215,1219-1232,1235,1237-1243,1245,1246,1249-1258,1260-1270,1273-1276,1278-1286,1288-1295,1297-1299,1302-1308,1312-1321,1323-1327,1329-1333,1335-1351,1353-1416,1418-1432,1435-1442,1444-1454,1456-1460,1462-1493,1495-1499,1502,1504-1520,1522,1523,1525-1532,1534-1555,1557-1579,1581,1582,1584-1593,1595-1599,1601-1640,1642-1657,1659-1665,1667-1686,1689-1699,1701-1716,1722,1724-1754,1756-1760,1762-1781,1784-1800,1802-1804,1806-1811,1813-1838,1841-1861,1865-1874,1876-1899,1901-1913,1915-1934,1936-1946,1948-1970,1973,1975-1983,1985-1997,2011,2012,2014-2019,2023-2029,2031,2032,2036,2037,2039,2044,2050-2064,2066,2067,2069-2098,2101,2102,2104,2108-2110,2112-2118,2120,2122-2125,2127-2134,2136-2143,2145-2159,2162-2169,2171-2178,2180-2189,2192-2195,2197-2199,2201-2221,2223-2250,2252-2259,2261-2287,2289-2300,2302-2322,2324-2365,2367-2380,2384-2392,2395-2398,2400,2402-2491,2493-2499,2501-2521,2523,2524,2526-2556,2558-2600,2603,2606,2609-2637,2639-2700,2703-2709,2711-2716,2719-2724,2726-2799,2801-2808,2810,2812-2868,2870-2874,2876-2908,2911-2919,2921-2966,2969-2997,2999,3002,3004,3008-3010,3012,3014-3016,3018-3029,3032-3051,3053-3070,3072-3076,3078-3127,3129-3167,3169-3210,3212-3220,3222-3259,3262-3267,3270-3282,3284-3299,3302-3305,3307-3321,3326-3332,3334-3350,3352-3366,3368,3373-3388,3391-3403,3405-3475,3477-3492,3494-3516,3518-3526,3528-3545,3547-3550,3552-3579,3581-3658,3660-3688,3691-3702,3704-3736,3738-3765,3767-3783,3785-3799,3802-3808,3810-3813,3815-3825,3829-3850,3852-3868,3870,3872-3877,3879,3881-3888,3890-3904,3906-3913,3915-3917,3919,3921-3944,3946-3970,3972-3985,3987-3994,3996,3997,3999,4007-4044,4046-4110,4112-4124,4127,4128,4130-4223,4225-4241,4243-4278,4280-4320,4322-4342,4344-4442,4447,4448,4450-4549,4551-4566,4568-4661,4663-4847,4849-4898,4901-4997,4999,5005-5008,5010-5029,5031,5032,5034-5049,5052,5053,5055-5059,5062-5079,5081-5086,5088-5099,5103-5119,5121-5189,5191-5199,5201-5213,5215-5220,5223,5224,5227-5268,5270-5279,5281-5297,5299-5356,5358-5404,5406-5413,5415-5430,5433-5439,5441-5499,5501-5509,5511-5543,5545-5549,5551-5554,5556-5559,5561-5565,5567-5630,5632,5634-5665,5667-5677,5680-5717,5719-5729,5731-5799,5803-5809,5812-5814,5816-5821,5823,5824,5826-5849,5851-5858,5860,5861,5863-5876,5878-5899,5905,5908,5909,5912-5914,5916-5921,5923,5924,5926-5949,5951,5953-5958,5964-5986,5990-5997,6008,6010-6024,6026-6058,6060-6099,6102-6105,6107-6111,6113-6122,6124-6128,6130-6155,6157-6345,6347-6388,6390-6501,6503-6509,6511-6542,6544-6546,6548-6564,6568-6579,6581-6645,6647-6665,6670-6688,6690,6691,6693-6698,6700-6778,6780-6787,6790,6791,6793-6838,6840-6880,6882-6900,6902-6968,6970-6999,7003,7005,7006,7008-7018,7020-7024,7026-7069,7071-7099,7101,7102,7104,7105,7107-7199,7202-7401,7403-7434,7436-7442,7444-7495,7497-7511,7513-7624,7626,7628-7675,7677-7740,7742-7776,7779-7799,7801-7910,7912-7919,7922-7936,7939-7998,8003-8006,8012-8020,8023-8030,8032-8041,8043,8044,8046-8079,8091,8092,8094-8098,8101-8179,8182-8191,8195-8199,8201-8221,8223-8253,8255-8289,8293-8299,8301-8332,8334-8382,8384-8399,8401,8403-8442,8444-8499,8501-8599,8601-8648,8650,8653,8655-8700,8702-8799,8801-8872,8874-8887,8889-8898,8900-8993,8995-8999,9004-9008,9012-9039,9041-9049,9051-9070,9072-9079,9082-9089,9092-9098,9104-9109,9112-9199,9201-9206,9208-9219,9221-9289,9291-9414,9416,9417,9419-9484,9486-9499,9501,9504-9534,9536-9574,9576-9592,9596-9617,9619-9665,9667-9875,9879-9897,9899,9901-9916,9918-9928,9930-9942,9945-9967,9969-9997,10005-10008,10011,10013-10023,10026-10081,10083-10179,10181-10214,10216-10242,10244-10565,10567-10615,10618-10620,10622-10625,10627,10630-10777,10779-11109,11112-11966,11968-11999,12001-12173,12175-12264,12266-12344,12346-13455,13457-13721,13723-13781,13784-13999,14001-14237,14239-14440,14443-14999,15001,15005-15659,15661-15741,15743-15999,16002-16011,16013-16015,16017,16019-16079,16081-16112,16114-16991,16994-17876,17878-17987,17989-18039,18041-18100,18102-18987,18989-19100,19102-19282,19284-19314,19316-19349,19351-19779,19781-19800,19802-19841,19843-19999,20001-20004,20006-20030,20032-20220,20223-20827,20829-21570,21572-22938,22940-23501,23503-24443,24445-24799,24801-25733,25736-26213,26215-26999,27001-27351,27354,27357-27714,27716-28200,28202-29999,30001-30717,30719-30950,30952-31037,31039-31336,31338-32767,32786-33353,33355-33898,33900-34570,34574-35499,35501-38291,38293-40192,40194-40910,40912-41510,41512-42509,42511-44175,44177-44441,44444-44500,44502-45099,45101-48079,48081-49151,49162,49164,49166,49168-49174,49177-49399,49401-49998,50004,50005,50007-50299,50301-50388,50390-50499,50501-50635,50637-50799,50801-51102,51104-51492,51494-52672,52674-52821,52823-52847,52849-52868,52870-54044,54046-54327,54329-55054,55057-55554,55556-55599,55601-56736,56739-57293,57295-57796,57798-58079,58081-60019,60021-60442,60444-61531,61533-61899,61901-62077,62079-63330,63332-64622,64624-64679,64681-64999,65001-65128,65130-65388,65390-65535" , host, "--rate=1000", "-e", interface], stdout=PIPE, stderr=PIPE)
		while True:
			if processDefault.poll() == 0:
				processDefault = processDefault.communicate()[0]
				ports = ""
				for v in re.findall(r'\d+\/tcp', processDefault):
					ports += v
				ports = ports.replace("/tcp", ",")
				ports = ports[:-1]
				if ports != "":
					currentDT = datetime.datetime.now()
					zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "			
					additionalTCP = 'Non-default TCP ports found, running additional scans...'
					print(Style.BRIGHT + Fore.YELLOW + zeTime + additionalTCP + Style.RESET_ALL)
					results = os.popen("nmap -sV -sC -p " + ports + " " + host + " " + output + "| head -n -3 | sed '1d;2d;3d;4d;'| tr '|' '-'| tr -d '_'").read()
					results = results.rstrip("\r\n")
					currentDT = datetime.datetime.now()
					zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "
					print(Style.BRIGHT + Fore.CYAN + zeTime + 'Non-default TCP Scan Report' + '\n' + '\n' + Style.RESET_ALL + results + '\n')
					os.system('stty sane')
				else:
					currentDT = datetime.datetime.now()
					zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "			
					noTCP = 'No non-default TCP ports found.'
         				print(Style.BRIGHT + Fore.YELLOW + zeTime + noTCP + Style.RESET_ALL)
					os.system('stty sane')
				break
			elif (processAll.poll() == 0) or (processAll.poll() == -15):
				processAll = processAll.communicate()[0]
				ports = ""
				for v in re.findall(r'\d+\/tcp', processAll):
					ports += v
				ports = ports.replace("/tcp", ",")
				ports = ports[:-1]
				if ports != "":
					currentDT = datetime.datetime.now()
					zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "			
					additionalTCP = 'Non-default TCP ports found, running additional scans...'
					print(Style.BRIGHT + Fore.YELLOW + zeTime + additionalTCP + Style.RESET_ALL)
					results = os.popen("nmap -sV -sC -p " + ports + " " + host + " " + output + "| head -n -3 | sed '1d;2d;3d;4d;'| tr '|' '-'| tr -d '_'").read()
					results = results.rstrip("\r\n")
					currentDT = datetime.datetime.now()
					zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "
					print(Style.BRIGHT + Fore.CYAN + zeTime + 'Non-default TCP Scan Report' + '\n' + '\n' + Style.RESET_ALL + results + '\n')
					os.system('stty sane')
				else:
					currentDT = datetime.datetime.now()
					zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "			
					noTCP = 'No non-default TCP ports found.'
         				print(Style.BRIGHT + Fore.YELLOW + zeTime + noTCP + Style.RESET_ALL)
					os.system('stty sane')
				break
		
	except:
		currentDT = datetime.datetime.now()
		zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "		
		massWrong = 'Something went wrong with the non-default TCP scan!' 		
		print('\n' + Style.BRIGHT + Fore.YELLOW + zeTime + massWrong + Style.RESET_ALL)
		os.system('stty sane')

#standard -sV -sC scan on the host
def nmapS():
	print(Style.BRIGHT + Fore.CYAN + '[+] ' + Style.RESET_ALL + 'Default TCP scan is running...')
	global output
	if output != "":
		output = output + " scouter --append-output"
	try:
		a=os.popen("nmap -sC -sV " + host + " " + output + "| head -n -3 | sed '1d;2d;3d;4d;'| tr '|' '-'| tr -d '_'").read()
		a=a.rstrip("\r\n")
		if a != "":
			currentDT = datetime.datetime.now()
			zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "
			print(Style.BRIGHT + Fore.CYAN + zeTime + 'Default TCP Scan Report' + '\n' + '\n' + Style.RESET_ALL + a + '\n')
			os.system("stty sane")
			return
		else:
			currentDT = datetime.datetime.now()
			zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "
			print(Style.BRIGHT + Fore.YELLOW + zeTime + 'No default TCP ports open? err...might want to check manually.' + Style.RESET_ALL + a)
			os.system("stty sane")
			return
	except:
		initialWrong = 'Something went wrong with the default TCP scan!'
		print(Style.BRIGHT + Fore.YELLOW + zeTime + initialWrong + Style.RESET_ALL)
		os.system('stty sane')
		return

#-sU --top-ports 500 --defeat-icmp-ratelimit scan on UDP
def udp():
	print(Style.BRIGHT + Fore.CYAN + '[+] ' + Style.RESET_ALL + 'Default UDP scan is running...\n')
	global output
	if output != "":
		output = output + " scouter --append-output"
	currentDT = datetime.datetime.now()
	zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "
	try:	
		b=os.popen("nmap -sU --top-ports 500 --defeat-icmp-ratelimit " + host + "|grep udp | grep -v 'open|filtered' | grep -v 'closed' | cut -d/ -f1 | tr '\n' ,").read()
		b=b.rstrip("\r\n")
		if b != "":
			currentDT = datetime.datetime.now()
			zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "			
			foundUDP = 'UDP ports found, running additional scans...'			
			print(Style.BRIGHT + Fore.YELLOW + zeTime + foundUDP + Style.RESET_ALL)
			result = os.popen("nmap -sU -sV -sC -p " + b + " " + host + " " + output + "| head -n -3 | sed '1d;2d;3d;4d;'| tr '|' '-'| tr -d '_'").read()
			result = result.rstrip("\r\n")
			currentDT = datetime.datetime.now()
			zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "
			print(Style.BRIGHT + Fore.CYAN + zeTime + 'UDP Scan Report' + '\n' + '\n' + Style.RESET_ALL + result + '\n')
			os.system("stty sane")
			return
     		else:
			currentDT = datetime.datetime.now()
			zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "			
			noUDP = 'No UDP ports found.'         		
			print(Style.BRIGHT + Fore.YELLOW + zeTime + noUDP + Style.RESET_ALL)
			os.system('stty sane')
			return
	except:
		currentDT = datetime.datetime.now()
		zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "		
		wrongUDP = 'Something went wrong with the UDP scan!'
		print('\n' + Style.BRIGHT + Fore.YELLOW + zeTime + wrongUDP + Style.RESET_ALL)
		os.system('stty sane')
		return

#-sU --top-ports 100 scan if the 'slow' flag is set
def slow():
	print(Style.BRIGHT + Fore.CYAN + '[+] ' + Style.RESET_ALL + 'Slow UDP scan is running...\n')
	global output
	if output != "":
		output = output + " scouter --append-output"
	try:
		b=os.popen("nmap -sU --top-ports 100 " + host + "|grep udp | grep -v 'open|filtered' | grep -v 'closed' | cut -d/ -f1 | tr '\n' ,").read()
		b=b.rstrip("\r\n")
		if b != "":
			currentDT = datetime.datetime.now()
			zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "			
			foundUDP = 'UDP ports found, running additional scans...'			
			print(Style.BRIGHT + Fore.YELLOW + zeTime + foundUDP + Style.RESET_ALL)
			result = os.popen("nmap -sU -sV -sC -p " + b + " " + host + output + "| head -n -3| sed '1d;2d;3d;4d;'| tr '|' '-'| tr -d '_'").read()
			result = result.rstrip("\r\n")
			currentDT = datetime.datetime.now()
			zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "
			print(Style.BRIGHT + Fore.CYAN + zeTime + 'UDP Scan Report' + '\n' + '\n' + Style.RESET_ALL + result + '\n')
			os.system('stty sane')
			return
     		else:
			currentDT = datetime.datetime.now()
			zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "			
			noUDP = 'No UDP ports found...'         		
			print(Style.BRIGHT + Fore.YELLOW + zeTime + noUDP + Style.RESET_ALL)
			os.system('stty sane')
			return
	except:
		currentDT = datetime.datetime.now()
		zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "		
		wrongUDP = 'Something went wrong with the UDP scan!'
		print('\n' + Style.BRIGHT + Fore.YELLOW + zeTime + wrongUDP + Style.RESET_ALL)
		os.system('stty sane')
		return

#feel free to uncomment this function call below if masscan is not quitting appropriately. This will kill masscan after 2 minutes. 
def cop():
	seconds = 0
	try:
		while seconds <= 140:
			time.sleep(10)
			seconds += 10
			if seconds == 130:
				os.popen("pkill -f masscan")
	except:
		currentDT = datetime.datetime.now()
		zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "
		wrongCop = 'Something went wrong with the "cop function!"' 		
		print('\n' + Style.BRIGHT + Fore.YELLOW + zeTime + wrongCop + Style.RESET_ALL)

if __name__=='__main__':
	print('\n')
	print(Style.BRIGHT + Fore.MAGENTA + '   _____                  __           ')
	print(Style.BRIGHT + Fore.MAGENTA + '  / ___/_________  __  __/ /____  _____     v.9001')
	print(Style.BRIGHT + Fore.MAGENTA + '  \__ \/ ___/ __ \/ / / / __/ _ \/ ___/')
	print(Style.BRIGHT + Fore.MAGENTA + ' ___/ / /__/ /_/ / /_/ / /_/  __/ /    ')
	print(Style.BRIGHT + Fore.MAGENTA + '/____/\___/\____/\__,_/\__/\___/_/     ' + Style.RESET_ALL)
	print('\n')
	if output !="":
		if output == "-oA":
			print(reportMessage1)
			print(reportMessage2)
			print(reportMessage3)
			print('\n')
		else:
			print(reportMessageNormal)
			print('\n')
	currentDT = datetime.datetime.now()
	zeTime = "[" + currentDT.strftime("%H:%M:%S") + "] "
	defaultScans = 'Initializing:'
	print(Style.BRIGHT + Fore.YELLOW + zeTime + defaultScans + Style.RESET_ALL)
	pnmap = Process(target = nmap)
	pnmap.start()
	#pcop = Process(target = cop)
	#pcop.start()	
	pnmapS = Process(target = nmapS)
	pnmapS.start()
	pudp = Process(target = udp)
	pslow = Process(target = slow)
	if args.slow:
		pslow.start()
	else:
		pudp.start()
