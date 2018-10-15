import sys, os, json
from receiver import GetELabEntries as labEntries, writeJSON

def getEntries(_libpath):
	_entries = json.loads(labEntries(_libpath))['entries']
	_experiments = json.loads(labEntries(_libpath, 'experiment'))['entries']
	result = list()

	titles = list(set([entry['title'] for entry in _entries]))
	for title in titles:
		entries = list(filter(lambda e: e['title'] == title, _entries))
		experiments = list(filter(lambda e: e['title'] == title, _experiments))
		for entry in entries:
			fittingExperiment = list(filter(lambda e: e['experimentday'] == entry['experimentday'], experiments))
			if len(fittingExperiment) > 0:
				if fittingExperiment[0]['description'] != "<p></p>":
					entry['experiment'] = fittingExperiment[0]['description']
				else:
					print('experiment bound, but with no content')
			else:
				print('no experiment found for {0} {1}'.format(entry['title'], entry['experimentday']))
			result.append(entry)
	return writeJSON(result)

if __name__ == '__main__':
	dirname  = os.path.dirname
	_libpath = dirname(dirname(os.path.realpath(__file__))) + '/lib/'
	getEntries(_libpath)