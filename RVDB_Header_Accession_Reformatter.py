# Reformats accessions in fasta headers to be compatible with the diff.
# This is a quick script. Filesnames are hardcoded.

import re

with open('v19headers.txt','r') as inFile:
	reader = inFile.readlines()
	with open('v19headers_formatted.txt', 'w') as outFile:
		for line in reader:
			if re.search('^>',line):
				try:
					pattern = re.search('\|(.+?)\|.*?(?P<name>[A-Za-z\t .\-\d+,]+)', line)
					gb = pattern.group(1)
					description = pattern.group(2)
					print(gb, file=outFile)
#					print('>'+gb+' '+description, file=outFile)
				except:
					print('Couldn\'t find for:',line)
