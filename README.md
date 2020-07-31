# RVDB
##### Standard pipeline for updating RVDB in HIVE.

The purpose of this workflow is to quickly update the RVDB Annotation Table in HIVE. The process of updating requires a connection to NCBI, which requires a pause at each query. Updating over 1.8 million lines in the table would therefore take around 100 hours, and because of the unstable connection to NCBI, requires the ability to track progress and manually restart at the last known position. In practice, this can take a month or more. Rather than updating the entire table, therefore, this pipeline is used to compare new additions to the table, and only retrive the content from NCBI for those accessions.

In addition, one of our sponsors requested a full lineage be included in the table (GenBank accessions only include a partial lineage). This pipeline therefore has 2 objectives: 1. update the existing table with new accessions, and 2. update the "Lineage" column to full taxonomic lineages. Once complete, the new additions are appended to the existing table, and the file is renamed. Taxonomic lineage update can be done using a local copy of the database, and therefore contact with NCBI is not required, but users are advised to update the table first (included in this pipeline). Example file inputs/outputs are given at each step, in this case updating from v.18 to v.19.

NOTE: I've been spot checking the files in between, but several of the scripts could be combined at this point.


---


#### 1. GET ALL v18 ACCESSIONS
RVDB_10June2020Update_Merged.tsv is the old RVDB 18.0 file. Take the gb column from this to get all of the accessions.

SCRIPT | 	INPUT FILE | OUTPUT FILE
-------|-------------|--------------
VDB_v18_AccessionGrabber.py | RVDB_10June2020Update_Merged.tsv | VDB_v18_Accessions.txt

Notes:
- The first line (column header) is excluded by looking for `=='gb'`

- Verify that this didn't pull anything else out by `wc -l` on the input and output files, there should only be 1 line difference.

---

#### 2. GET ALL v19 HEADERS
Accessions that will be used for comparison are in the RVDB v18 file. The first step is to pull them out of the headers from the fasta file.

COMMAND:

  `grep ">" HIVE_C-RVDBv19.0_curated.fasta > v19headers_2.txt`

Note: Can also use `^>` instead of `>` in the grep command.

---

#### 3. FORMAT CONVERSION
Convert to accession numbers.

SCRIPT | INPUT FILE | OUTPUT FILE
-------|------------|------------
RVDB_Header_Accession_Reformatter.py | v19headers.txt | v19headers_formatted.txt

---

#### 4. SORT FILES
Sort files for easier comparison.


COMMANDS:
<br>`sort VDB_v18_Accessions.txt > VDB_v18_Accessions_Sorted.txt`
<br>`sort v19headers_formatted.txt > v19headers_formatted_Sorted.txt`

---

#### 5. COMPARISON
Compare the list of accessions taken from the v18 table and v19 fasta file.

COMMAND:
<br>`git diff --color VDB_v18_Accessions_Sorted.txt v19headers_formatted_Sorted.txt | egrep '^.[[[:digit:]]+m\+' | less -R > v18_v19_diff_Sorted_condensed_colors.txt`

<br><h6><i>&nbsp;&nbsp;&nbsp;NOTE: I moved this to my local machine to write code for the next step in an IDE and discovered that it doesn't like the color codes. This next command strips the colors out, if needed:</i></h6>

<br>COMMAND:
<br>`sed 's/\x1b\[[0-9;]*m//g' v18_v19_diff_Sorted_condensed_colors.txt > v16_v18_diff_Sorted_condensed_no_colors.txt`

<br><h6><i>&nbsp;&nbsp;&nbsp;See the really great first answer at the below URL for more info: https://superuser.com/questions/380772/removing-ansi-color-codes-from-text-stream</i></h6>

---
