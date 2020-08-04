import pandas as pd
pd.options.display.max_colwidth = 1000
pd.set_option("display.max_columns", 10)
with open ('duplicateList.txt', 'w') as outFile:
	data = pd.read_csv("C-RVDBv19_31July2020_Merged.tsv", dtype={'refSeq': str}, sep = '\t')
	df = pd.DataFrame(data)
	print (df['refSeq'][df.duplicated(subset=['refSeq'],keep=False)], file = outFile)