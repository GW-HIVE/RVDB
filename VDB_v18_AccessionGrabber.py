import csv

with open('RVDB_10June2020Update_Merged.tsv', 'r') as inFile:
		with open('VDB_v18_Accessions.txt', 'w') as outFile:
				read_tsv = csv.reader(inFile, delimiter = "\t")
				for row in read_tsv:
						if row[5] == 'gb':
							pass
						else:
							print (row[5], file=outFile)
