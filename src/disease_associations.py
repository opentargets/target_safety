import argparse
import json
from helpers import *


def get_assocs_info(associations_file,rare_diseases_list,EFO_names):

	# Parses the Open Targets associations file and the list of rare diseases (output from `rare_diseases.py`) to collect the following
	# for diseases which are highly associated with each target
	# (>= 0.75 overall association score, direct associations only):
	# (i) therapeutic areas these diseases belong to,
	# (ii) whether they are marked as a rare disease.

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
					rare_disease_assocs.setdefault(target,[]).append({'code':disease,'label':EFO_names[disease]})

		for target in therapeutic_areas:
			therapeutic_areas[target] = [{'code':disease,'label':EFO_names[disease]} for disease in list(therapeutic_areas[target])]

	return(therapeutic_areas,rare_disease_assocs)


def get_cancer_genes(cosmic_evidence_file,EFO_names):

	# Parses the OT cosmic evidence file to flag targets that are marked as cancer genes from COSMIC
	# and collects information on tier (COSMIC) and the known mutations per disease

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

			cosmic.setdefault(target,{'tier':tier,'evidence':[]})['evidence'].append({'disease_code':disease,'disease_label':EFO_names[disease],'known_mutations':mutations})

	return(cosmic)

def rare_diseases_from_file(rare_diseases_file):

	# Reads in rare diseases file into a list

	rare_diseases_list = []
	with open(rare_diseases_file,'r') as rarefile:
		for line in rarefile:
			rare_diseases_list.append(line.split()[0])
	return(rare_diseases_list)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-OT_associations", help="Open Targets associations filename.", required=True)
	parser.add_argument("-cosmic", help="Latest COSMIC evidence file submitted to Open Targets.", required=True)
	parser.add_argument("-rare","--rare_diseases", help="Text file with rare diseases list (EFO terms).", required=True)
	parser.add_argument("-EFO_mapfile", help="Json file with disease terms and names.", required=True)
	parser.add_argument("-o","--output", help="Output json filename", required=True)
	args = parser.parse_args()

	# read in rare diseases list
	rare_diseases_list = rare_diseases_from_file(args.rare_diseases)

	# dictionary with EFO labels to names
	EFO_names = get_EFO_names(args.EFO_mapfile)

	# get therapeutic areas and rare diseases for associations per target
	therapeutic_areas,rare_disease_assocs = get_assocs_info(args.OT_associations,rare_diseases_list,EFO_names)

	# add cancer driver/suppressor info
	cancer_genes = get_cancer_genes(args.cosmic,EFO_names)

	# combine into a single output
	combined = {'Info_D1:therapeutic_areas_high_assocs': therapeutic_areas,'Bucket_D1:rare_disease_high_assocs': rare_disease_assocs, 'Bucket_D2:cancer_genes': cancer_genes}
	disease_assoc_buckets = combine_dicts_genekey(combined)
	write_json_file(disease_assoc_buckets,args.output)
