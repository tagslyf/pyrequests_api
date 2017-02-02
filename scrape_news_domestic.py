# -*- coding: utf-8 -*-
import json, os, random, requests, time
from bs4 import BeautifulSoup


def scrape_news_domestic():
	url = "http://temp.163.com/special/00804KVA/cm_guonei.js?callback=data_callback"
	fetch = requests.get(url)
	fetch_json = eval(fetch.text[14:-1])
	for news in fetch_json:
		remove_file = False
		title = news['title']
		filename = news['docurl']
		filename = filename.split("/")
		filename = filename[len(filename) - 1].replace(".html", "")
		article = requests.get(news['docurl'])
		if article.status_code == 200:
			article_html = BeautifulSoup(article.text, "html.parser")
			if article_html.find("div", {'id': "endText"}):
				with open("contents/{}.txt".format(filename), "w", encoding="utf-8") as f:
					for p in article_html.find("div", {'id': "endText"}).findAll("p", attrs={'class': None})[:3]:
						if p.string is not None:
							f.write("	{}\n\n".format(p.string))
						else:
							remove_file = True
				if remove_file:
					os.remove("contents/{}.txt".format(filename))


if __name__ == "__main__":
	print("Scraping of news.163.com/domestic is running...")
	while True:
		scrape_news_domestic()
		time.sleep(600)