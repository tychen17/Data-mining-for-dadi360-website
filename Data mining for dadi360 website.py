#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd


# In[2]:


base_url = 'http://c.dadi360.com'


# In[3]:


def get_links(start_page, end_page):
    links = set()
    for i in range(start_page-1, end_page):
        url = base_url + '/c/forums/show/' + str(90 * i) + '/57.page'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_links = [a['href'] for a in soup.select('a[href^="/c/posts/list/"]')]
        links.update(page_links)  
    return list(links) 

def format_phone_number(phone_number):
    digits = re.sub(r'\D', '', phone_number)
    digits = (digits + '0000000000')[:10]
    formatted = '(' + digits[:3] + ') ' + digits[3:6] + '-' + digits[6:]
    return formatted

def scrape_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.select_one('div.subject').get_text(strip=True)
    title = title.replace('文章主题:', '').strip()
    content = soup.select_one('div.postbody').get_text(strip=True)
    
    phone_regex = re.compile(r'\b1?[-.]?(\d{3}[-.]?\d{3}[-.]?\d{4}|\(\d{3}\)[-.]?\d{3}[-.]?\d{4})\b')
    phone_numbers = re.findall(phone_regex, soup.text)
    phone_numbers = list(set([format_phone_number(num) for num in phone_numbers]))

    return title, content, phone_numbers


# In[4]:


start_page = 1 # Change this to adjust the start page
end_page = 2 # Change this to adjust the end page
links = get_links(start_page, end_page)


# In[5]:


data_list = []

for link in links:
    title, content, phone_numbers = scrape_info(base_url + link)
    for phone_number in phone_numbers:
        data_list.append({'title': title, 'phone_number': phone_number, 'content': content})


# In[6]:


with open('output.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['title', 'content', 'phone_number']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in data_list:
        writer.writerow(data)


# In[7]:


df = pd.read_csv('output.csv')
df


# In[8]:


locations = ['曼哈顿', '纽约', '长岛', '新泽西', '皇后区','皇后','法拉盛']
def find_location(row):
    title = row['title']
    content = row['content']
    location_found = []

    for location in locations:
        if pd.notna(title) and re.search(r'\b' + location + r'\b', title):
            location_found.append(location)
        if pd.notna(title) and re.search(location + r'\b', title):
            location_found.append(location)
        if pd.notna(title) and re.search(r'\b' + location, title):
            location_found.append(location)
        elif pd.notna(content) and re.search(r'\b' + location + r'\b', content):
            location_found.append(location)
        elif pd.notna(content) and re.search(location + r'\b', content):
            location_found.append(location)
        elif pd.notna(content) and re.search(r'\b' + location, content):
            location_found.append(location)
    return ', '.join(location_found) if location_found else 'NA'


# In[9]:


df['location'] = df.apply(find_location, axis=1)
df.to_csv('output_with_location.csv', index=False, encoding='utf-8-sig')


# In[10]:


df2 = pd.read_csv('output_with_location.csv')
df2


# In[ ]:




