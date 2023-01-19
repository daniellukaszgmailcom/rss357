#!/usr/bin/python3
import requests
from slugify import slugify
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from dateutil import parser
from pytz import timezone

# Script was written in cooperation with ChatGPT: openai.com
# Script should be executed at least once a day - at about 0:00
# libraries to install (pip3 install XXX): requests slugify bs4 feedgen.feed dateutil pytz
# The feeds will be written in the file below. The website below will be scanned:
file_add = 'RADIO357-gpt.xml'
url = 'https://radio357.pl/twoje357/audycje/'

# Make a GET request to the website to get the HTML
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the links to the audition pages
audition_links = []
for div in soup.find_all('div', {'class': 'my357Cover'}):
    a_elements = div.find_all('a', href=True)
    for a in a_elements:
        audition_links.append('https://radio357.pl'+a['href'])

# Create a new RSS feed
fg = FeedGenerator()
fg.id(url)
fg.title('New Podcasts from Radio357')
fg.author({'name': 'Radio357', 'email': 'info@radio357.pl'})
fg.link(href=url, rel='alternate')
fg.logo('https://radio357.pl/wp-content/uploads/2019/11/cropped-357-32x32.png')
fg.description('New podcasts from Radio357')

# Create a list to store all podcasts
all_podcasts = []

# Iterate over each audition page
for link in audition_links:
    # Make a GET request to the audition page
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find all the podcast elements on the page
    podcast_elements = soup.find_all('div', {'class': 'podcastBody'})
    podcast_name = soup.title.string.replace(" - Radio357", "")

    # Add each podcast to the all_podcasts list
    for element in podcast_elements:
        title = element.find('h3').text
        try:
            description = element.find('div', {'class': 'podcastDesc'}).text
        except:
            description = 'No description available'
        date_string = element.find('div', {'class': 'podcastTime'}).text
        date = parser.parse(date_string.split(',')[0], dayfirst=True)
        all_podcasts.append({'title': title, 'description': description, 'date': date, 'link': link, 'podcast_name': podcast_name})

# Sort the all_podcasts list by date
all_podcasts.sort(key=lambda x: x['date'], reverse=False)
utc = timezone('UTC')

# Add the latest 100 podcasts to the RSS feed
for podcast in all_podcasts[-100:]:
    podcast['date'] = utc.localize(podcast['date'])
    fe = fg.add_entry()
    fe.title(podcast['podcast_name'] + ' - ' + podcast['title'])
    fe.description(podcast['description'])
    fe.guid(podcast['link']+'#'+slugify(podcast['title']), permalink=True)
    fe.link(href=podcast['link']+'#'+slugify(podcast['title']))
    fe.pubDate(podcast['date'].strftime('%a, %d %b %Y %H:%M:%S %z'))

# Generate the RSS feed XML
rssfeed = fg.rss_str(pretty=True)

# Write the XML to a file
with open(file_add, 'wb') as f:
    f.write(rssfeed)
