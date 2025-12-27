#!/usr/bin/env python
# coding: utf-8

# In[32]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 
from datetime import date


# In[34]:


URL = "https://corporate.ethiopianairlines.com/AboutEthiopian/careers/results"
Headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36" ,"Accept-Encoding": "gzip, deflate, br, zstd",  "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1" }

page = requests.get(URL, headers = Headers)

soup = BeautifulSoup(page.content, "html.parser")


results = []
scrape_time = date.today()
scrape_time_iso = scrape_time.isoformat()
job_items = soup.find_all("li")

for item in job_items:
    header = item.find("div", class_="card-header")
    if not header:
        continue  # not a real posting

    # Extract simple text fields
    title_tag = header.find("strong", string=lambda x: x and "Postion" in x)
    location_tag = header.find("strong", string=lambda x: x and "Location" in x)
    announcement_tag = header.find("strong", string=lambda x: x and "Announcement" in x)

    # Clean values
    def clean_next_text(tag):
        if not tag:
            return None
        # text is often inside the next_sibling
        return tag.next_sibling.strip().replace("\xa0", " ")

    job_title = clean_next_text(title_tag)
    location = clean_next_text(location_tag)
    announcement = clean_next_text(announcement_tag)

    # Move into the collapsible body (candidate part)
    panel_body = item.find("div", class_="panel-body")
    candidate_list = []
    # 1) Locate the DATE & TIME section
    date_time_p = None
    
    for p in item.find_all("p"):
        u = p.find("u")
        if u and "DATE & TIME" in u.get_text(strip=True).upper():
            date_time_p = p
            break
    
    # 2) Extract the actual date/time values
    if date_time_p:
        date_parts = [b.get_text(" ", strip=True) for b in date_time_p.find_all("b")]
        date_time = " ".join(date_parts) if date_parts else None
    else:
        date_time = None

    if panel_body:
        table = panel_body.find("table")
        if table:
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    # td0 = index, td1 = candidate name
                    candidate_name = cols[1].get_text(strip=True)
                    candidate_list.append(candidate_name)

    results.append({
        "job_title": job_title,
        "location": location,
        "scrape_time": scrape_time_iso,
        "date_time": date_time,
        "announcement": announcement,
        "candidates": candidate_list,
        
    })

df_new = pd.DataFrame(results)
if os.path.exists("result.jsonl"):
    df_old = pd.read_json("result.jsonl", lines = True)
else:
    df_old = pd.DataFrame(columns=df_new.columns)

# === 6. Merge and remove duplicates (by Position + Registration Date) ===
df_combined = pd.concat([df_old, df_new], ignore_index=True)
df_clean = df_combined.drop_duplicates(subset=["job_title", "announcement","location","date_time"])

# === 7. Save the updated file ===
df_clean.to_json("result.jsonl", orient="records", lines= True ,index=False)

