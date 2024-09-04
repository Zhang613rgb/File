import os
import re
import sys
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_connectable(url, timeout=5):
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Connection to {url} failed: {e}")
        return False

def get_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve HTML from {url}: {e}")
        return ''

def _get_avsox_urls() -> list:
    try:
        html = get_html('https://tellme.pw/avsox')
        soup = BeautifulSoup(html, 'html.parser')
        urls = [a['href'] for a in soup.select('h4 strong a')]
        return urls
    except Exception as e:
        logging.error(f"Failed to retrieve URLs from avsox: {e}")
        return []

def _get_javbus_urls() -> list:
    try:
        html = get_html('https://www.javbus.one/')
        text = html
        urls = re.findall(r'防屏蔽地址：(https://(?:[\d\w][-\d\w]{1,61}[\d\w]\.){1,2}[a-z]{2,})', text, re.I | re.A)
        return urls
    except Exception as e:
        logging.error(f"Failed to retrieve URLs from javbus: {e}")
        return []

def _get_javlib_urls() -> list:
    try:
        html = get_html('https://github.com/javlibcom')
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.find('div', class_='p-note user-profile-bio mb-3 js-user-profile-bio f4')
        if text:
            match = re.search(r'[\w\.]+', text.get_text(), re.A)
            if match:
                domain = f'https://www.{match.group(0)}.com'
                return [domain]
    except Exception as e:
        logging.error(f"Failed to retrieve URLs from javlib: {e}")
        return []

def _get_javdb_urls() -> list:
    try:
        html = get_html('https://jav523.app')
        soup = BeautifulSoup(html, 'html.parser')
        js_links = [script['src'] for script in soup.find_all('script', src=True)]
        for link in js_links:
            if '/js/index' in link:
                js_content = get_html(link)
                match = re.search(r'\$officialUrl\s*=\s*"(https://(?:[\d\w][-\d\w]{1,61}[\d\w]\.){1,2}[a-z]{2,})"', js_content, flags=re.I | re.A)
                if match:
                    return [match.group(1)]
    except Exception as e:
        logging.error(f"Failed to retrieve URLs from javdb: {e}")
        return []

def _choose_one(urls) -> str:
    for url in urls:
        if is_connectable(url):
            return url
    return ''

if __name__ == "__main__":
    results = []
    
    # 获取各网站的免代理地址
    javdb_urls = _get_javdb_urls()
    javlib_urls = _get_javlib_urls()
    
    # 将结果添加到列表中
    if javdb_urls:
        results.append(f'javdb:\t{javdb_urls}')
    if javlib_urls:
        results.append(f'javlib:\t{javlib_urls}')
    
    # 将结果保存到文件
    with open('jav.txt', 'w', encoding='utf-8') as f:
        for line in results:
            f.write(f"{line}\n")
    
    # 打印结果到控制台
    for line in results:
        logging.info(line)
