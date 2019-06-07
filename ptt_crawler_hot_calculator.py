#!/usr/bin/env python
#coding:utf-8

# Project Name: PTT熱門度計算機
# Created date: 2019/06/07
# Description: 使用Python requests, beautifulsoup 實作PTT爬蟲，並計算關鍵字在該看板之熱門度

# import modules
import requests
from bs4 import BeautifulSoup
import json
import sys

# 關鍵字、看版、頁數設定
keyword = 'offer'
board = 'Soft_job'
pages = 10

# 爬蟲初始設定(看版網址、已刪除文章置換、所有文章list)
start = 'https://www.ptt.cc/bbs/' + board + '/index.html'
deleted = BeautifulSoup('<a>本文已被刪除</a>', 'lxml').a
all_posts = list()

# 取得目前文章屬性
def GetCurrentPagePostInfo(url):
	global all_posts
	
	# 設定已滿18歲cookie
	response = requests.get(url = url, cookies = {'over18': '1'})

	# 爬蟲設定
	soup = BeautifulSoup(response.text, 'lxml')
	articles = soup.find_all('div', 'r-ent')

	# 取出所有文章並加到all_posts(list)中
	for article in articles:
		meta = article.find('div', 'title').find('a') or deleted
		if meta != deleted and meta.getText().lower().strip().find(keyword) > 0:
			all_posts.append({
				'title': meta.getText().strip(),
				'link': meta.get('href'),
				'push': article.find('div', 'nrec').getText(),
				'date': article.find('div', 'date').getText(),
				'author': article.find('div', 'author').getText(),
				'score': 0
				})

	# 取得下一頁連結
	control_btn = soup.find('div', 'btn-group-paging').find_all('a', 'btn')
	next_page = control_btn[1].get('href')
	return next_page

# 還原完整網址
def GenerateUrl(link):
	return 'https://www.ptt.cc' + link

# 取得文章內容、屬性
def GetContent(link):
	url = GenerateUrl(link)
	
	response = requests.get(url = url, cookies = {'over18': '1'})
	soup = BeautifulSoup(response.text, 'lxml')

	content = soup.find('div', 'bbs-screen')
	time = content.find_all('div', 'article-metaline')[2].find('span', 'article-meta-value')
	push = content.find_all('span', 'push-tag')

	# 幹圖here
	#img = content.find_all('a')
	# save and download maybe

	return push

# 開始爬蟲
for i in range(pages):
	# debug log
	print(start)

	next_page = GetCurrentPagePostInfo(start)
	start = GenerateUrl(next_page)

# 計算關鍵字熱門度(推文+1分、噓文-1分)
total_score = 0

for post in all_posts:
	try:
		for element in GetContent(post['link']):
			if element.getText().find('推') > -1:
				post['score'] += 1
			elif element.getText().find('噓') > -1:
				post['score'] -= 1
	except:
		print('some error occured')

	# debug log
	print(json.dumps(post, ensure_ascii = False))

	total_score += int(post['score'])

print('Total Score: ' + str(total_score))