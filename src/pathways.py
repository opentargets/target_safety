import json
from helpers import *
from flag_GO_React_terms import *



if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-gene_index", help="Open Targets gene index contents", required=True)
	parser.add_argument("-go", help="filename of list with enriched GO terms to flag", required=True)
	parser.add_argument("-react", help="filename of list with enriched Reactome terms to flag", required=True)
	parser.add_argument("-o", "--output", help="Output json filename", required=True)
	args = parser.parse_args()

	# Genes with flagged GO/Reactome terms
	flagged_genes = flag_genes(args.gene_index, args.go, args.react)

	# Add AOP data here (& anything else pathway-related) and then in the combined dictionary.

	# Combine the above into biological function json safety information.
	combined = {'Bucket_P1:flagged_GO_or_Reactome_term': flagged_genes}
	biological_function_buckets = combine_dicts_genekey(combined)

	write_json_file(biological_function_buckets,args.output)
