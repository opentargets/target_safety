import argparse
from helpers import *
import pandas as pd

def consolidate(esslist):
	translate_ess_acronym = {
		"E": "Essential",
		"F": "Fitness",
		"NE": "Nonessential",
		"UD": "Unknown",
		"ND": "Unknown"}
	ess_types = list(set(esslist))
	if len(ess_types) > 1:
	    return('Conditional')
	else:
	    return(translate_ess_acronym[ess_types[0]])

def consolidate_ogee_data(ogee_file):
	# same as original consolidated file
	ogee_df = pd.read_csv(ogee_file,sep='\t')
	translate_essential_terms = {
	    "NE": "NE",
	    "GA": "NE",
	    "E": "E",
	    "D": "E",
	    "ES": "E",
	    "DE": "E",
	    "NE,E-infection": "E",
	    "NE,E-infection,E-co-infection": "E",
	    "NE,E-co-infection": "E",
	    "NE,F-infection,E-co-infection": "E",
	    "NE,E-infection,F-co-infection": "E",
	    "F": "F",
	    "GD": "F",
	    "NE,F-co-infection": "F",
	    "NE,F-infection": "F",
	    "NE,F-infection,F-co-infection": "F",
	    "ND": "ND",
	    "U": "ND"}

	ogee_df['essential']=ogee_df['essential'].str.translate(translate_essential_terms)
	ogee_df = ogee_df.drop(['#taxID','sciName','dataType','dataSource'],axis='columns')
	ogee_df = pd.DataFrame(ogee_df.groupby(['locus'])['essential'].apply(list))
	ogee_df['core_fitness'] = ogee_df['essential'].apply(consolidate)
	ogee_df = ogee_df[(ogee_df['core_fitness'] != "Nonessential") & (ogee_df['core_fitness'] != "Unknown")]
	cf_ogee = ogee_df.drop(['essential'],axis='columns').to_dict(orient='index')
	for gene in cf_ogee:
		cf_ogee[gene]['ref_link'] = 'http://ogee.medgenius.info/browse'

	return(cf_ogee)

def make_cf_dict(sangerfile,broadfile,bagelfile,ogeefile,hgnc_to_ensembl):

	with open(sangerfile,'r') as sanger:
		cf_sanger = sanger.read().splitlines()
	# completely skipping over genes that are not mapped for now
	cf_sanger = {hgnc_to_ensembl[hgnc]:{'core_fitness': 'Essential','ref_link':'https://score.depmap.sanger.ac.uk'} for hgnc in cf_sanger if hgnc in hgnc_to_ensembl}

	with open(broadfile, 'r') as broad:
		cf_broad = broad.read().splitlines()
	cf_broad = {hgnc_to_ensembl[hgnc]:{'core_fitness': 'Essential','ref_link':'https://score.depmap.sanger.ac.uk'} for hgnc in cf_broad if hgnc in hgnc_to_ensembl}

	with open(bagelfile, 'r') as bagel:
		cf_bagel = [line.split()[0] for line in bagel]
	cf_bagel = {hgnc_to_ensembl[hgnc]:{'core_fitness': 'Essential','ref_link':'http://tko.ccbr.utoronto.ca'} for hgnc in cf_bagel if hgnc in hgnc_to_ensembl}

	# with open(ogeefile, 'r') as ogee:
	# 	cf_ogee = {}
	# 	for line in ogee:
	# 		line = line.strip().split(',')
	# 		flag = line[-1]
	# 		if flag != 'Nonessential': # we are including 'Conditional' information
	# 			cf_ogee[line[0]] = {'core_fitness': flag, 'ref_link':'http://ogee.medgenius.info/browse'}



		#cf_ogee = [hgnc_to_ensembl[hgnc] for hgnc in cf_bagel if hgnc in hgnc_to_ensembl]
	cf_ogee = consolidate_ogee_data(ogeefile)

	combined = {'Sanger': cf_sanger,'Broad': cf_broad, 'BAGEL': cf_bagel, 'OGEE': cf_ogee}
	combined = combine_dicts_genekey(combined)

	return(combined)

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-sanger", help="File with core fitness genes based on Sanger binary dependency scores (https://score.depmap.sanger.ac.uk/downloads)", required=True)
	parser.add_argument("-broad", help="File with core fitness genes based on Broad binary dependency scores (https://score.depmap.sanger.ac.uk/downloads)", required=True)
	parser.add_argument("-bagel", help="File with core fitness genes from Toronto KnockOut Library (http://tko.ccbr.utoronto.ca)", required=True)
	parser.add_argument("-ogee", help="File with consolidated human core fitness genes from OGEE (http://ogee.medgenius.info/browse/Homo sapiens)", required=True)
	parser.add_argument("-gene_mapfile", help="Open Targets HGNC gene symbol to ENSEMBL gene id json file", required=True)
	parser.add_argument("-o", "--output", help="Output json filename", required=True)
	args = parser.parse_args()

	hgnc_to_ensembl = Ensembl_from_HGNC(args.gene_mapfile)
	combined = make_cf_dict(args.sanger,args.broad,args.bagel,args.ogee,hgnc_to_ensembl)
	write_json_file(combined,args.output)
