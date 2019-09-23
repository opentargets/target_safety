import argparse
import pandas as pd
import json
from helpers import *



def collect_terms(flagged_terms_tsv):

	import pandas as pd

	df = pd.read_csv(flagged_terms_tsv,sep='\t')
	header = list(df.columns)

	terms = []
	for col in header:
		terms.append(list(df[col].dropna()))

	return(header,terms)

def flag_genes(gene_index, flagged_GO_terms_tsv, flagged_Reactome_terms_tsv):

	import json

	GO_header,GO_terms = collect_terms(flagged_GO_terms_tsv)
	React_header,React_terms = collect_terms(flagged_Reactome_terms_tsv)

	flagged_genes = {}
	with open(gene_index) as genefile:
		for line in genefile:
			annot = json.loads(line)
			#annot = json.loads(line)['_source'] 
			ensembl_id = annot['ensembl_gene_id']

			# GO terms
			go_annot = annot['go']
			for entry in go_annot:
				for idx in range(len(GO_header)):
					if entry['id'] in GO_terms[idx]:
						flagged_genes.setdefault(ensembl_id, {}).setdefault('GO_safety_flags',{}).setdefault(GO_header[idx],[])
						#flagged_genes[ensembl_id]['GO_safety_flags'][GO_header[idx]].append(entry['id']) # if we don't need the rest
						flagged_genes[ensembl_id]['GO_safety_flags'][GO_header[idx]].append({'term_id':entry['id'],'term_name':entry['value']['term']})


			# Reactome terms
			react_annot = annot['reactome']
			for entry in react_annot:
				for idx in range(len(React_header)):
					if entry['id'] in React_terms[idx]:
						flagged_genes.setdefault(ensembl_id, {}).setdefault('Reactome_safety_flags',{}).setdefault(React_header[idx],[])
						#flagged_genes[ensembl_id]['Reactome_safety_flags'][React_header[idx]].append(entry['id']) # if we don't need the rest
						flagged_genes[ensembl_id]['Reactome_safety_flags'][React_header[idx]].append({'term_id':entry['id'],'term_name':entry['value']['pathway name']})

	return(flagged_genes)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-gene_index", help="Open Targets gene index contents")
	parser.add_argument("-go", help="filename of list with enriched GO terms to flag")
	parser.add_argument("-react", help="filename of list with enriched Reactome terms to flag")
	parser.add_argument("-o", "--output", help="Output json filename")
	args = parser.parse_args()

	flagged_genes = flag_genes(args.gene_index, args.go, args.react)
	write_json_file(flagged_genes,args.output)
