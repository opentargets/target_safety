import argparse
import json
from helpers import *


def get_assocs_info(associations_file,rare_diseases_list):

	with open(associations_file) as infile:
		therapeutic_areas = {}
		rare_disease_assocs = {}
		for line in infile:
			entry = json.loads(line)
			target = entry['target']['id']
			disease = entry['disease']['id']
			thareas = entry['disease']['efo_info']['therapeutic_area']['codes']
			is_direct = entry['is_direct']
			score = entry['association_score']['overall']

			if is_direct and score >= 0.75:
				therapeutic_areas.setdefault(target,set()).update(thareas)

				if disease in rare_diseases_list:
					rare_disease_assocs.setdefault(target,[]).append(disease)

		for target in therapeutic_areas:
			therapeutic_areas[target] = list(therapeutic_areas[target])

	return(therapeutic_areas,rare_disease_assocs)


def get_cancer_genes(cosmic_evidence_file):
	with open(cosmic_evidence_file) as infile:
		cosmic = {}
		for line in infile:
			entry = json.loads(line)
			target = entry['target']['id'].split('/')[-1]
			disease = entry['disease']['id'].split('/')[-1]
			tier = entry['target']['tier']
			mutations = [{'pref_mutation_name':mut['preferred_name'],
						  'role_in_cancer':mut['role_in_cancer'],
						  'inheritance_pattern':mut['inheritance_pattern']}
						 for mut in entry['evidence']['known_mutations']]

			cosmic.setdefault(target,{}).setdefault('tier',tier)
			cosmic[target].setdefault('diseases',{}).setdefault(disease,[]).extend(mutations)
	return(cosmic)

def rare_diseases_from_file(rare_diseases_file):
	rare_diseases_list = []
	with open(rare_diseases_file,'r') as rarefile:
		for line in rarefile:
			rare_diseases_list.append(line.split()[0])
	return(rare_diseases_list)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-OT_associations", help="Open Targets associations filename.")
	parser.add_argument("-cosmic", help="Latest COSMIC evidence file submitted to Open Targets.")
	parser.add_argument("-rare","--rare_diseases", help="Text file with rare diseases list (EFO terms).")
	parser.add_argument("-o","--output", help="Output json filename")
	args = parser.parse_args()

	# read in rare diseases list
	rare_diseases_list = rare_diseases_from_file(args.rare_diseases)

	# get therapeutic areas and rare diseases for associations per target
	therapeutic_areas,rare_disease_assocs = get_assocs_info(args.OT_associations,rare_diseases_list)

	# add cancer driver/suppressor info
	cancer_genes = get_cancer_genes(args.cosmic)

	# combine into a single output
	combined = {'Info_D1:therapeutic_areas_high_assocs': therapeutic_areas,'Bucket_D1:rare_disease_high_assocs': rare_disease_assocs, 'Bucket_D2:cancer_genes': cancer_genes}
	disease_assoc_buckets = combine_dicts_genekey(combined)
	write_json_file(disease_assoc_buckets,args.output)
