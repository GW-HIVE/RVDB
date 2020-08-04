import csv

with open ("RVDB_v19_correctedLineage.tsv", newline="") as inFile:
	with open ("RVDB_10June2020Update_Merged.tsv", 'a') as outFile:
		tsvFile = csv.reader(inFile, delimiter = "\t")
		for line in inFile:
			print(line.strip(), file = outFile)

inFile.close()