#!/usr/bin/env python
# coding: utf-8

# In[11]:


import requests
import pandas as pd
from bs4 import BeautifulSoup 
import datetime
import os


# In[13]:


URL = "https://corporate.ethiopianairlines.com/AboutEthiopian/careers/vacancies"
Headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36" ,"Accept-Encoding": "gzip, deflate, br, zstd",  "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1" }

page = requests.get(URL , headers = Headers)
soup = BeautifulSoup(page.content, "html.parser")

intional_jobs = soup.find("div", id= "Contentplaceholder3_C190_Col00")
job_cards = intional_jobs.find_all("div" , class_= "card-header")

scrape_time = datetime.date.today()

jobs= []

for card in job_cards:
    job= {}
    for field in ["Position","Location","Closing Date"]:
        strong = card.find("strong", string = lambda s: s and field in s)

        if strong:
            value = strong.next_sibling
            while value and (value.name or not str(value).strip()):
                value = value.next_sibling
            job[field] = value.strip() if value else None

        else:
            job[field] = None

    job["Scrape date"] = scrape_time
    jobs.append(job)


df = pd.DataFrame(jobs)
print (df)

df_new = pd.DataFrame(jobs)

# === 5. Check if jobs.csv exists ===
if os.path.exists("injobs.csv"):
    df_old = pd.read_csv("injobs.csv")
else:
    df_old = pd.DataFrame(columns=df_new.columns)

# === 6. Merge and remove duplicates (by Position + Registration Date) ===
df_combined = pd.concat([df_old, df_new], ignore_index=True)
df_clean = df_combined.drop_duplicates(subset=["Position", "Closing Date"])

# === 7. Save the updated file ===
df_clean.to_csv("injobs.csv", index=False)


# In[ ]:




