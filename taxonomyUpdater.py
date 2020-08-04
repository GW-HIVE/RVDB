import csv
from ete3 import NCBITaxa

ncbi = NCBITaxa()

with open('annotationTable_RVDB19_FullLineages.tsv', newline='') as tsvin, open('correctedLineage_VDB_v19.tsv', 'w', newline='') as csvout:
	tsvin = csv.reader(tsvin, delimiter='\t')
	csvout = csv.writer(csvout, delimiter='\t')
	for line in tsvin:
		try:
			taxid = line[3]
			lst=[]
			lineage=ncbi.get_lineage(taxid)
			lineageNames = ncbi.get_taxid_translator(lineage)

		# Format the names according to annotation table format.
			for node in lineage:
				nodeName = lineageNames[node].rstrip()
				lst.append(nodeName)
			lineageFormatted=(("[{0}]".format('; '.join(map(str, lst)))))

		except:
			lineageFormatted=line

		csvout.writerow([line[0], line[1], line[2], line[3], lineageFormatted[1:-1], line[5], line[6], line[7], line[8]])
