import json, os, random, requests, sys, threading, time, uuid
from base64 import b64encode
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from lxml import etree
from os import listdir
from os.path import isfile

lock = threading.Lock()


def request_api(name, url, headers, proxys, proxymesh_ip, limit_errors=False):
	desc = "{}\n\n\n{}"
	title = '大奖娱乐【邮件限时专享优惠】'
	
	top = "大奖娱乐【邮件限时专享优惠】：首存100送108共获208，15倍流水即可！ 更多小额福利：存20可获得48！存50可获得108！新春好礼送不停，详情请见 http://www.djlaohuji.com"
	headers['X-ProxyMesh-IP'] = proxymesh_ip

	errors = {}
	for i in range(req_limit):
		try:
			img = random.choice(image_urls)
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
				'title': title,
				'description': desc.format(top, news).replace('.', '&#46;')
			}
			response = requests.post(url, headers=headers, data=data, proxies=proxys, timeout=5)
			if response.status_code == 200:
				response_data = response.json()['data']
				link = "{}{}".format(domain, response_data['id'])
				links.append(link)
				with open("saveContent.txt", "a", encoding="utf-8") as f:
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


def proxymesh_api():
	global contents, domain, image_urls, titles, req_limit, start, promos
	pid = str(uuid.uuid4()).upper().replace("-", "")[:16]
	domain = "http://imgur.com/"
	write_upload_log("Start", pid, "Start API request using proxmesh proxy.")
	image_urls = ["http://i.imgur.com/nRTNo6y.png", "http://oi64.tinypic.com/jtvuxf.jpg", "http://thumbsnap.com/i/e5bvtDl8.png?0118"]
	req_limit = 100
	start = datetime.now()
	threads_num = 2	
	# Call proxymesh api to get the proxy list
	url = "https://proxymesh.com/api/proxies/"
	username = "winner88"
	password = "qweasd321"
	response = requests.get(url, auth=requests.auth.HTTPBasicAuth(username, password))

	if response.status_code == 200:
		url = "https://api.imgur.com/3/image"
		headers = {}
		headers['Authorization'] = "Client-ID e8e0297762a5593"
		proxymesh_proxies = response.json()['proxies']
		for proxymesh_proxy in proxymesh_proxies:
			proxys = {
				'http': 'http://winner88:qweasd321@{}'.format(proxymesh_proxy),
				'https': 'http://winner88:qweasd321@{}'.format(proxymesh_proxy)
			}
			proxymesh_ips = []
			for n in range(1, 176):
				try:
					response = requests.get('http://httpbin.org/ip', proxies=proxys, timeout=5)
				except Exception as ex:
					pass
				else:
					if 'X-ProxyMesh-IP' in response.headers:
						if response.headers['X-ProxyMesh-IP'] not in proxymesh_ips:
							proxymesh_ips.append(response.headers['X-ProxyMesh-IP'])
			proxy_counter = 0
			write_upload_log(proxymesh_ips, 'API', '{} Proxymesh current IP address given.'.format(len(proxymesh_ips)))
			while True:
				threads = []
				for i in range(threads_num):
					proxymesh_ip = proxymesh_ips[proxy_counter]
					t = threading.Thread(target = request_api, args = ("ProxyMeshThread-{}".format(i), url, headers, proxys, proxymesh_ip, False))
					threads.append(t)
					t.start()
					proxy_counter += 1
					if proxy_counter >= len(proxymesh_ips):
						break
				for t in threads:
					t.join()
				if proxy_counter >= len(proxymesh_ips):
					break
		write_upload_log("Stop", pid, "Proccessing for proxymesh proxies' is stop. Links total count is {}".format(len(links)))
	else:
		write_upload_log("None", "None", "Error on getting proxies in {}".format(url))
		write_upload_log("Stop", pid, "Proccessing for proxymesh proxies' is stop. Links total count is {}".format(len(links)))


def write_upload_log(ip, username, message):
	with open("data/proxymesh_uploadlog_{}.txt".format(datetime.now().strftime("%Y%m%d")), "a") as f:
		f.write("{}	{}	{}	{}\n".format(datetime.now(), ip, username, message))


if __name__ == "__main__":
	print("Start imgur upload using proxymesh.com proxies.")
	global links
	links = []
	while True:
		proxymesh_api()
		time.sleep(300)