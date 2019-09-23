import json
from helpers import *
from essential_genes import *
from flag_GO_React_terms import *



if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-gene_index", help="Open Targets gene index contents")
	parser.add_argument("-go", help="filename of list with enriched GO terms to flag")
	parser.add_argument("-react", help="filename of list with enriched Reactome terms to flag")
	parser.add_argument("-sanger", help="File with core fitness genes based on Sanger binary dependency scores (https://score.depmap.sanger.ac.uk/downloads)")
	parser.add_argument("-broad", help="File with core fitness genes based on Broad binary dependency scores (https://score.depmap.sanger.ac.uk/downloads)")
	parser.add_argument("-bagel", help="File with core fitness genes from Toronto KnockOut Library (http://tko.ccbr.utoronto.ca)")
	parser.add_argument("-ogee", help="File with human core fitness genes from OGEE (http://ogee.medgenius.info/browse/Homo sapiens)")
	parser.add_argument("-gene_mapfile", help="Open Targets HGNC gene symbol to ENSEMBL gene id json file")
	parser.add_argument("-o", "--output", help="Output json filename")
	args = parser.parse_args()

	# Genes with flagged GO/Reactome terms
	flagged_genes = flag_genes(args.gene_index, args.go, args.react)

	# Essential genes info
	hgnc_to_ensembl = Ensembl_from_HGNC(args.gene_mapfile)
	essential = make_cf_dict(args.sanger,args.broad,args.bagel,args.ogee,hgnc_to_ensembl)

	# Combine the above into biological function json safety information.
	combined = {'Bucket_B1:core_fitness_gene': essential,'Bucket_B2:flagged_GO_or_Reactome_term': flagged_genes}
	biological_function_buckets = combine_dicts_genekey(combined)

	write_json_file(biological_function_buckets,args.output)
