# RVDB
##### Standard pipeline for updating RVDB in HIVE.

The purpose of this workflow is to quickly update the RVDB Annotation Table in HIVE. The process of updating requires a connection to NCBI, which requires a pause at each query. Updating over 1.8 million lines in the table would therefore take around 100 hours, and because of the unstable connection to NCBI, requires the ability to track progress and manually restart at the last known position. In practice, this can take a month or more. Rather than updating the entire table, therefore, this pipeline is used to compare new additions to the table, and only retrive the content from NCBI for those accessions.

In addition, one of our sponsors requested a full lineage be included in the table (GenBank accessions only include a partial lineage). This pipeline therefore has 2 objectives: 1. update the existing table with new accessions, and 2. update the "Lineage" column to full taxonomic lineages. Once complete, the new additions are appended to the existing table, and the file is renamed. Taxonomic lineage update can be done using a local copy of the database, and therefore contact with NCBI is not required, but users are advised to update the table first (included in this pipeline). Example file inputs/outputs are given at each step, in this case updating from v.18 to v.19.

See [overview image](https://github.com/GW-HIVE/RVDB/blob/master/RVDB_Annotation_Workflow.png), but note that it's generalized (no specific file names).

NOTE: I've been spot checking the files in between, but several of the scripts could be combined at this point.


---


#### 1. GET ALL ACCESSIONS FROM OLD DB (v18 here)
RVDB_10June2020Update_Merged.tsv is the old RVDB 18.0 file. Take the gb column from this to get all of the accessions.

SCRIPT | 	INPUT FILE | OUTPUT FILE
-------|-------------|--------------
VDB_v18_AccessionGrabber.py | RVDB_10June2020Update_Merged.tsv | VDB_v18_Accessions.txt

Notes:
- Remember to invoke it with `python3`, not `python`!
- The first line (column header) is excluded by looking for `=='gb'`
- You'll have to update the file reference, it's hard coded (refers to previous project's folder to prevent duplicating the large file).
- Verify that this didn't pull anything else out by `wc -l` on the input and output files, there should only be 1 line difference.

---

#### 2. GET ALL NEW HEADERS (v19 here)
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

<br><h6><i>NOTE: I moved this to my local machine to write code for the next step in an IDE and discovered that it doesn't like the color codes. This next command strips the colors out, if needed:</i></h6>

<br>COMMAND:
<br>`sed 's/\x1b\[[0-9;]*m//g' v18_v19_diff_Sorted_condensed_colors.txt > v18_v19_diff_Sorted_condensed_no_colors.txt`

<br><h6><i>See the really great first answer at the below URL for more info: https://superuser.com/questions/380772/removing-ansi-color-codes-from-text-stream</i></h6>

---

#### 6. GET ALL GenBank INFO FOR THE NEW ENTRIES
Switch to my local machine for this (server is having some trouble with ETE3).
Gather all of the necessary GenBank info for any v18 accessions not already represented in the v16 table. Files are in the "Update_[n]" folder (current n = 4).


SCRIPT | INPUT FILE | OUTPUT FILES
-------|------------|-------------
SequenceRetriever20.py | v18_v19_diff_Sorted_condensed_no_colors.txt | annotationTable_RVDB19_FullLineages_[n].tsv
|      |            | ErrorLog_[n].txt
|      |            | progressLog_[n].txt


Usage note: This script has to contact NCBI for data. The connection frequently drops, so it's built to be able to pick up where you left off. The error log is used to keep track of any errors along the way, and the progress log is used to keep track of where the script left off. There's a line in the script that's used as the starter location (line 56). The last line of the progress file is used as the number in this field. The associated files that were produced are also named with that starting number. For example, if the script leaves off at line 1176, then the next script will start at position 1176, and that value will be used for [n] in naming the three files, like:
<br>"annotationTable_RVDB18_FullLineages_1176.tsv," "ErrorLog_1176.txt," and "progressLog_1176.txt." <strong>You will have to remove the header line from the input file.</strong>

<h6><i>NOTE: There is also a portion that gives a progress indicator (the block starting at line 34 and then the block starting at line 207). When we started using the much smaller versions of this script I stopped using this because it might only take the script ~1 hour or so to run, so it's a lot less necessary than before. If you plan to use it for longer jobs, it might need a little tweaking to run proplery.</i></h6>

In this case, the values for n were:
<br>		0 - 1830
<br>		1831 - 9812

Files were manually stitched together by grabbing all of 1-1830 and pasting them into the other to create annotationTable_RVDB19_FullLineages.tsv

Depending on the nature of the errors, you may need to manually address some of them. Often I see errors because the script is unable to pull the "host" value (because it doesn't exist in the GB record). That's unimportant for our purposes, so I ignore them.

---

#### 7. UPDATE THE TAXONOMY DATABASE
Revising the taxonomy lineages in the annotation table does not require contact with NCBI because it can be done using a local copy of the file. However, the database must be up to date before carrying that step out. It can be done either at the command line on linux, or using a script (which was done for my local machine). To run it locally, enter the python environment and enter the 3 commands in the script manually.

SCRIPT:
`TaxDB_Updater.py`

---

#### 8. REFORMAT LINEAGES INTO FULL LINEAGES
This takes the 'TaxonID' column from the table and uses it to retrieve the full lineage using ETE3.
Full lineage is used to replace the existing truncated lineages in the table.

SCRIPT | INPUT FILE | OUTPUT FILE
-------|------------|------------
taxonomyUpdater.py | annotationTable_RVDB19_FullLineages.tsv | correctedLineage_VDB_v19.tsv

Note that this script needs to be corrected, the header gets the wrong output. Should say:
'Lineage'

---

#### 9. MERGE DATA FOR NEW ENTRIES INTO THE EXISTING TABLE
Just open up the existing RVDB v19 table (as append only) and append the new table to it, line by line.
It is recommended to make a backup of the existing RVDB table before executing this script, just to be safe.

SCRIPT | INPUT FILE | OUTPUT FILE
-------|------------|------------
tableMerge.py | RVDB_v19_correctedLineage.tsv | RVDB_10June2020Update_Merged.tsv

Once finished, rename the file [C/U]-RVDBv[version #]_[date as ddmonthyyyy]_Merged.tsv
E.g. C-RVDBv19_31July2020_Merged.tsv
Do a line length check on the file using `wc -l`, make sure that the number of lines equals the sum of the two that were merged into one.

---

#### 10. CHECK FOR DUPLICATES
If any of the entries in the new table (19 in this case) already existed in the previous table (18 in this case), they would not be detected.

SCRIPT:
`DuplicateCheck.py`

---

#### 11. GENERATE THE HIT LIST IN HIVE
1. In HIVE, uplload the tsv file (RVDB_10June2020Update_Merged.tsv, in this case) and the select it in the.
2. Go to Convert > to annotation
3. Use TargetLength for start and end positions, and RefSeq for the third field.
4. Check the box under it for use all fields. Don't do anything else, just submit.

---

