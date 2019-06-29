import requests
import pandas as pd
import os
import simplejson as json
import reportermate as rm
import codecs

# Check if we already have a current gender paygap file

current_exists = os.path.isfile('current.csv')

if current_exists:
	os.rename('current.csv', 'old.csv')

# Get data

thisYear = "https://gender-pay-gap.service.gov.uk/viewing/download-data?year=2019"
lastYear = "https://gender-pay-gap.service.gov.uk/viewing/download-data?year=2018"

print("Downloading data...")
r = requests.get(thisYear)

with open('current.csv', 'w') as f:
		f.write(r.text)

# Make sure we have the previous years data for comparison

lastyear_exists = os.path.isfile('lastYear.csv')

if not lastyear_exists:
	print("Getting last year's data...")
	r = requests.get(lastYear)
	with open('lastYear.csv', 'w') as f:
			f.write(r.text)

if lastyear_exists:
	print("Already got last year's data, no need to download again")

# Compare new and old data, make new csv with the new companies only 

current = pd.read_csv('current.csv')
# old = pd.read_csv('old.csv')
old = pd.read_csv('old-test.csv')

lastyear = pd.read_csv('lastYear.csv')

lastyear['period'] = '2018-19'
current['period'] = '2019-20'

# Newly reporting companies since last time we checked

key_diff = set(current.EmployerName).difference(old.EmployerName)
where_diff = current.EmployerName.isin(key_diff)

new = current[where_diff]

# Get figures from last year for the new companies

new_ly = lastyear.loc[lastyear['EmployerName'].isin(new.EmployerName)]

new_ly.to_csv('new-ly.csv', index=False)
new.to_csv('new.csv', index=False)

# Change in percentage points from last year

combined = pd.concat([new, new_ly], ignore_index=True)
combined.sort_values(['period'], inplace=True)
combined['difference'] = combined[['DiffMedianHourlyPercent','EmployerName']].groupby(['EmployerName'], as_index=False).diff()

# Flag important companies

with open("important.json") as json_file:
	important = json.load(json_file)

def isImportant(row):
    if row['EmployerName'] in important:
    	return "yes"

combined['important'] = combined.apply(isImportant, axis=1)

# Save CSV

combined.to_csv('combined.csv', index=False)

# Run reportermate

story = rm.analyseAndRender('combined.csv','paygap-template.txt')
print(story)
with codecs.open("story.txt", "w", encoding='utf8') as f:
	f.write(story)

