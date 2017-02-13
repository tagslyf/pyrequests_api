#!/bin/bash

python scrape_news_domestic.py &
python proxymesh.py &
python gatherproxy.py &
python scrapeproxy.py