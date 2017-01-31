#!/bin/bash

python scrape_news_domestic.py &
python gatherproxy.py &
python scrapeproxy.py