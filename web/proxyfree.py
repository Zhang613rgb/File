import os
import re
import sys
import logging
import socket
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_connectable(url, timeout=5):
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
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

def get_proxy_free_url(site_name: str, prefer_url=None) -> str:
    if prefer_url and is_connectable(prefer_url):
        return prefer_url
    
    site_name = site_name.lower()
    func_name = f'_get_{site_name}_urls'
    get_funcs = [i for i in dir(sys.modules[__name__]) if i.startswith('_get_')]
    if func_name in get_funcs:
        get_urls = getattr(sys.modules[__name__], func_name)
        try:
            urls = get_urls()
            return _choose_one(urls)
        except Exception as e:
            logging.error(f"Failed to get proxy-free URL for {site_name}: {e}")
            return ''
    else:
        raise Exception(f"Don't know how to get proxy-free URL for {site_name}")

def _choose_one(urls) -> str:
    for url in urls:
        if is_connectable(url):
            return url
    return ''


def _get_avsox_urls() -> list:
    try:
        html = get_html('https://tellme.pw/avsox')
        urls = html.xpath('//h4/strong/a/@href')
        return urls
    except Exception as e:
        logging.error(f"Failed to retrieve URLs from avsox: {e}")
        return []


def _get_javbus_urls() -> list:
    try:
        html = get_html('https://www.javbus.one/')
        text = html.text_content()
        urls = re.findall(r'防屏蔽地址：(https://(?:[\d\w][-\d\w]{1,61}[\d\w]\.){1,2}[a-z]{2,})', text, re.I | re.A)
        return urls
    except Exception as e:
        logging.error(f"Failed to retrieve URLs from javbus: {e}")
        return []


def _get_javlib_urls() -> list:
    try:
        html = get_html('https://github.com/javlibcom')
        text = html.xpath("//div[@class='p-note user-profile-bio mb-3 js-user-profile-bio f4']")[0].text_content()
        match = re.search(r'[\w\.]+', text, re.A)
        if match:
            domain = f'https://www.{match.group(0)}.com'
            return [domain]
    except Exception as e:
        logging.error(f"Failed to retrieve URLs from javlib: {e}")
        return []


def _get_javdb_urls() -> list:
    try:
        html = get_html('https://jav523.app')
        js_links = html.xpath("//script[@src]/@src")
        for link in js_links:
            if '/js/index' in link:
                text = get_resp_text(request_get(link))
                match = re.search(r'\$officialUrl\s*=\s*"(https://(?:[\d\w][-\d\w]{1,61}[\d\w]\.){1,2}[a-z]{2,})"', text, flags=re.I | re.A)
                if match:
                    return [match.group(1)]
    except Exception as e:
        logging.error(f"Failed to retrieve URLs from javdb: {e}")
        return []


if __name__ == "__main__":
    results = []
    javdb_urls = _get_javdb_urls()
    javlib_urls = _get_javlib_urls()
    
    if javdb_urls:
        results.append(f'javdb:\t{javdb_urls}')
    if javlib_urls:
        results.append(f'javlib:\t{javlib_urls}')
    
    with open('jav.txt', 'w', encoding='utf-8') as f:
        for line in results:
            f.write(f"{line}\n")
    
    for line in results:
        logging.info(line)
