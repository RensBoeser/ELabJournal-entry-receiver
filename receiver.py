import requests, json, re, csv, time

def __main__(libpath):
	# get token using login details from eLabJournal stored in a json
	token = APIKEY( json.loads( open('{0}\\secrets.json'.format(libpath)).read() ) )
	
	# download entries
	entries = getSections(token, 'entry')

	# generate json file containing entries
	writeJSON(entries, libpath)
	
	# generate csv file containing entries
	# writeCSV(entries)

def APIKEY(secrets):
	url = 'https://www.elabjournal.com/api/v1/auth/user'
	data = dict(
		username=secrets["username"],
		password=secrets["password"]
	)

	response = requests.post(url=url, data=data)
	# print(str(response) + " | " + url)
	return response.json()['token']

def request(API_key, url, data=None):
	if data: response = requests.get(url=url, data=data, headers=dict(Authorization=API_key))
	else: response = requests.get(url=url, headers=dict(Authorization=API_key))
	
	# print(str(response) + " | " + url)
	return response.json()

def date_converter(date):
	# change [yyyy-mm-dd] to [MONTH dd]
	date  = date.split('-')
	monthNames = {"01": "Januari",
								"02": "Febuari",
								"03": "March",
								"04": "April",
								"05": "May",
								"06": "June",
								"07": "July",
								"08": "August",
								"09": "September",
								"10": "October",
								"11": "November",
								"12": "December"
							}

	day   = date[2]
	month = monthNames.get(date[1])

	return month + ' ' + day

def getSections(token, identifier, type="paragraph"):
	if   type == "paragraph":
		return getParagraphSections(token, identifier)
	else:
		print("type '{0}' not yet compatible".format(type))
	

def getParagraphSections(token, identifier):
	print('downloading notebook entries...')
	start = time.time()

	# get all experiments (where the user is a contributor of)
	entries = list()
	experiments = request(token, 'https://www.elabjournal.com/api/v1/experiments')['data']
	for experiment in experiments:
		experimentID = experiment['experimentID']
		# print(str(experimentID) + ' | ' + experiment['name'])

		# get all sections within every experiment
		sections_url = 'https://www.elabjournal.com/api/v1/experiments/{0}/sections'.format(experimentID)
		sections = request(token, sections_url)['data']
		for section in sections:
			# get all sections that have a title containing the identifier
			if identifier in section['sectionHeader']:
				content_url = 'https://www.elabjournal.com/api/v1/experiments/{0}/sections/{1}/content'.format(experimentID, section['expJournalID'])
				content = request(token, content_url)['contents']
				# generate entry in dictionary form
				entry = dict(
					title=experiment['name'],
					date=section['sectionDate'].split('T')[0], # remove the timestamp
					attendees="UNKNOWN", # TODO: find out how to get attendees from the API
					description=content,
					category="wetlab",
					experimentday=re.search(r'\d+', section['sectionHeader']).group()
				)
				entries.append(entry)
				# print("- " + str(section['expJournalID']) + " | " + entry['title'] + " " + entry['experimentday'] + " (" + entry['date'] + ")") #FOR DEBUGGING#
	
	# document downloadtime
	end = time.time()
	print('downloaded notebook entries [{0}ms]'.format(int((end-start) * 1000)))
	
	# sort entries and formulate monthnames
	entries = sorted(entries, key=lambda k: k['date'])
	for i in range(len(entries)): entries[i]['date'] = date_converter(entries[i]['date'])

	return entries

def writeJSON(entries, outFolder, outFile="wetlab-entries"):
	if type(entries) == list:
		with open(outFolder + '\\' + outFile + '.json', 'w') as f:
			f.write('{\n')
			f.write('\t"entries": [\n\t\t')
			for i in range(len(entries)):
				json.dump(entries[i], f)
				if not i == len(entries)-1:
					f.write(',\n\t\t')
			f.write('\n\t]\n}')
	else:
		print("incompatible value for 'entries'")
	
def writeCSV(entries, outFolder, outFile="wetlab-entries"):
	if type(entries) == list:
		with open(outFolder + '\\' + outFile + '.csv', 'w', newline='') as f:
			writer = csv.writer(f)
			# header row
			writer.writerow(['date'] + 
											['title'] + 
											['attendees'] + 
											['description'] + 
											['category'] + 
											['experimentday']
			)
			# data rows
			for entry in entries:
				writer.writerow([entry['date']] + 
												[entry['title']] + 
												[entry['attendees']] + 
												[entry['description']] + 
												[entry['category']] + 
												[entry['experimentday']]
				)
	else:
		print("incompatible value for 'entries'")

if __name__ == '__main__':
	__main__()