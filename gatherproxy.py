import json, os, random, requests, sys, threading, time, uuid
from base64 import b64encode
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from os import listdir
from os.path import isfile

lock = threading.Lock()


def request_api(name, url, headers, proxys, proxymesh_ip, limit_errors=False):
	desc = "{}\n\n\n{}"
	title = ""
	content_header = ""
	headers['X-ProxyMesh-IP'] = proxymesh_ip

	errors = {}
	for i in range(req_limit):
		try:
			random.shuffle(titles)
			title = random.choice(titles)
			img = random.choice(image_urls)
			random.shuffle(content_headers)
			content_header = random.choice(content_headers)
			while True:
				news = os.listdir("contents/")
				random.shuffle(news)
				news = random.choice(news)
				with open("contents/{}".format(news), "r") as f:
					news = f.read()
				if news.strip() != "None":
					break
			data = {
				'image': img,
				'title': title.replace('.', '&#46;'),
				'description': desc.format(content_header, news).replace('.', '&#46;')
			}
			response = requests.post(url, headers=headers, data=data, proxies=proxys, timeout=5)
			if response.status_code == 200:
				response_data = response.json()['data']
				link = "{}{}".format(domain, response_data['id'])
				links.append(link)
				# with open("saveContent.txt", "a", encoding="utf-8") as f:
				with open("saveContent.txt", "a") as f:
					f.write("{}\n".format(link))
				print("{}".format(link))
				write_upload_log(proxymesh_ip, 'API:{}'.format(name), link)
			elif response.status_code == 400 and "You are uploading too fast" in response.json()['data']['error']:
				write_upload_log(proxymesh_ip, 'API', "{} {}".format(response, response.json()['data']['error']))
				break
			elif "Imgur is temporarily over capacity" in response.json()['data']['error']:
				write_upload_log(proxymesh_ip, 'API', "{} {}".format(response, response.json()['data']['error']))
				break
			else:
				write_upload_log(proxymesh_ip, 'API', "Error response: {} {}".format(response, response.json()['data']['error']) if response.json() else response.text)
		except Exception as ex:
			type, value, traceback = sys.exc_info()
			if limit_errors:
				if type.__name__ not in errors:
					for element, index in enumerate(errors):
						errors[index] = 0
					errors[type.__name__] = 1
				else:
					if errors[type.__name__] >= 25:
						write_upload_log(proxymesh_ip, 'API', "Error encountered 25 times: {}@{} line#{} {}".format(type.__name__, name, traceback.tb_lineno, value))
						break
					else:
						errors[type.__name__] += 1
			write_upload_log(proxymesh_ip, 'API', "REQUESTS ERROR: {}({}@{} line#{}) - {}".format(type.__name__, name, i + 1, traceback.tb_lineno, value))
			if type.__name__ in ['SSLError', 'ProxyError']:
				break


def checkproxy(name, gather_proxy, counter):	
	url = 'http://httpbin.org/ip'
	proxies = {
		'http': 'http:{}'.format(gather_proxy),
		'https': 'http:{}'.format(gather_proxy),
	}
	try:
		rsp = requests.get(url, proxies=proxies, timeout=3)
	except Exception as e:
		pass
	else:
		if gather_proxy not in ok2get_proxy:
			ok2get_proxy.append(gather_proxy)
	lock.acquire()
	lock.release()


def check_gatherproxy():
	global gather_proxies, ok2get_proxy
	gather_proxies = []
	ok2get_proxy = []
	with open("gather_proxy.txt", "r") as f:
		for proxy in f:
			gather_proxies.append(proxy.rstrip())
	start = datetime.now()
	threads_num = 30
	counter = 0
	proxyloop = True
	while proxyloop:
		threads = []
		for i in range(threads_num):
			proxy = gather_proxies[counter]
			t = threading.Thread(target = checkproxy, args = ("Thread-{}".format(i), proxy, counter))
			threads.append(t)
			t.start()
			counter += 1
			if counter >= len(gather_proxies):
				proxyloop = False
				break
		for t in threads:
			t.join()
	return ok2get_proxy


def gatherproxy_api():
	global content_headers, domain, image_urls, req_limit, start, titles
	pid = str(uuid.uuid4()).upper().replace("-", "")[:16]
	domain = "http://imgur.com/"
	write_upload_log("Start", pid, "Start API request using gather proxies.")
	content_headers = []
	with open("content_headers.txt", "r") as f:
		for ch in f.readlines():
			content_headers.append(ch.rstrip())
	image_urls = []
	with open("banner_urls.txt", "r") as f:
		for url in f.readlines():
			image_urls.append(url.rstrip())
	titles = []
	with open("titles.txt", "r") as f:
		for title in f.readlines():
			titles.append(title.rstrip())
	checked_proxies = check_gatherproxy()
	proxy_counter = 0
	proxyloop = False
	req_limit = 100
	start = datetime.now()
	start_time = time.time()
	threads_num = 2
	url = "https://api.imgur.com/3/image"
	headers = {}
	headers['Authorization'] = "Client-ID e8e0297762a5593"
	write_upload_log(checked_proxies, 'API', '{} Gathered proxies current IP address.'.format(len(checked_proxies)))
	while True:
		threads = []
		for i in range(threads_num):
			proxy_ip = checked_proxies[proxy_counter]
			proxys = {
				'http': 'http://{}'.format(proxy_ip),
				'https': 'https://{}'.format(proxy_ip)
			}
			t = threading.Thread(target = request_api, args = ("GatherProxyThread-{}".format(i), url, headers, proxys, proxy_ip, True))
			threads.append(t)
			t.start()
			proxy_counter += 1
			if proxy_counter >= len(checked_proxies):
				proxyloop = True
				break
		for t in threads:
			t.join()
		if proxyloop:
			break
	write_upload_log("Stop", pid, "Proccessing for gather proxies' is stop. Links total count is {}".format(len(links)))


def write_upload_log(ip, username, message):
	with open("data/gatherproxy_uploadlog_{}.txt".format(datetime.now().strftime("%Y%m%d")), "a") as f:
		f.write("{}	{}	{}	{}\n".format(datetime.now(), ip, username, message))


if __name__ == "__main__":
	print("Start imgur upload using gatherproxy proxies.")
	global links
	links = []
	while True:
		gatherproxy_api()