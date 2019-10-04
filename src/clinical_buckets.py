import argparse
from helpers import *
from drug_info import *
from known_target_safety import *
from FDA_AEs_per_target import *


def clinical_buckets(drug_index,known_safety_adr,known_safety_sri,known_safety_ubr,known_safety_efo,known_safety_ref,fda_aes_by_target,gene_mapfile):

	# Collect clinical findings bucket info into a combined json file

	# Get withdrawn drugs, black box warning, and drug phase frequency data
	drug_label_info = collect_drug_label_info(drug_index,bbox_text=False)

	# Get known target safety information
	known_target_safety = generate_known_safety_json(known_safety_adr,known_safety_sri,known_safety_ubr,known_safety_efo,known_safety_ref,gene_mapfile)

	# Get openFDA significant adverse event per target information
	AEs_per_target = get_AEs_per_target(fda_aes_by_target)

	# Combine everything into one dictionary using Ensembl Gene IDs as the keys.
	combined = {'drug_label_info':drug_label_info,'Bucket_C3:known_target_safety':known_target_safety,'Bucket_C4:openFDA_AEs':AEs_per_target}
	clinical_findings = combine_dicts_genekey(combined)

	return(clinical_findings)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-drug_index", help="Open Targets drug index contents", required=True)
	parser.add_argument("-adr","--adverse_effects", help="tsv of manually curated adverse effects per target", required=True)
	parser.add_argument("-sri","--safety_risk_info", help="tsv of manually curated safety risk information per target", required=True)
	parser.add_argument("-ubr","--uberon_mapping", help="tsv with uberon mapping for tissues in adverse effect and safety info spreadsheets", required=True)
	parser.add_argument("-efo","--efo_mapping", help="tsv with efo mapping for terms in adverse effect spreadsheet", required=True)
	parser.add_argument("-ref","--references", help="tsv with reference information for entries in adverse effect and safety info spreadsheets", required=True)
	parser.add_argument("-fda_aes","--fda_aes_by_target", help="significant openFDA adverse events PER TARGET", required=True)
	parser.add_argument("-gene_mapfile", help="Open Targets HGNC gene symbol to ENSEMBL gene id json file", required=True)
	parser.add_argument("-o","--output", help="Output json filename", required=True)
	args = parser.parse_args()

	clinical_findings = clinical_buckets(args.drug_index,args.adverse_effects,args.safety_risk_info,args.uberon_mapping,args.efo_mapping,args.references,args.fda_aes_by_target,args.gene_mapfile)
	write_json_file(clinical_findings,args.output)
