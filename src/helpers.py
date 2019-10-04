def read_json_file(json_file):

	# reads in json file

	import json
	with open(json_file) as injson:
		data = json.load(injson)

	return(data)


def write_json_file(data,json_file):

	# writes json file pretty-printed

	import json
	with open(json_file, 'w') as f:
		json.dump(data, f,indent=4)
		#json.dump(data, f)

def Ensembl_from_HGNC(mapfile):

	# reads file with gene name info to make look-up dictionary in the format:
	# {HGNC_symbol : ENSEMBL_ID}

	import json
	hgnc_to_ensembl = {}
	with open(mapfile) as map:
		for line in map:
			line = json.loads(line)
			hgnc_to_ensembl[line['hgnc_approved_symbol']] = line['ensembl_id']

	return(hgnc_to_ensembl)

def get_EFO_names(disease_mapfile):

	# reads file with disease name info to make look-up dictionary in the format:
	# {EFO_code : disease_full_name}

	import json
	EFO_names = {}
	with open(disease_mapfile) as map:
		for line in map:
			line = json.loads(line)
			EFO_names[line['efo_id']] = line['disease_full_name']

	return(EFO_names)

# use if map file not available?
def switch_to_EnsemblIDs(mydict, gene_index, type = 'from_symbols'):

	# NOT USED
	# gene symbols for now, add whatever else is needed
	import json

	genemap = {}
	with open(gene_index) as genefile:
		for line in genefile:
			annot = json.loads(line)
			ensemblID = annot['ensembl_gene_id']
			if type == 'from_symbols':
				init_id = annot['approved_symbol']
				genemap[init_id] = ensemblID
			# add whatever other type we'll need (e.g. uniprot)

	return(genemap)


def combine_dicts_genekey(combined):

	# Merges input dictionaries that have overlapping keys (in this case, ENSEMBL gene id) (outer join), under these keys
	# EXAMPLE:
	# if we have the dictionaries:
	# drug_label_info = {'ENSG12345':drug content1, 'ENSG67890':drug content2} and
	# known_target_safety = {'ENSG54321':known content1, 'ENSG67890':known content2}
	# define as INPUT to the function the combined dict:
	# combined = {'drug_label_info': drug_label_info,'known_target_safety': known_target_safety,...}
	# Then the output will be:
	# outdict = {'ENSG12345':{'drug_label_info':drug content1},
	#            'ENSG67890':{'drug_label_info':drug content2,'known_target_safety':known content2}
	#            'ENSG54321':{'known_target_safety':known content1}
	#            }

	from collections import defaultdict

	outdict = defaultdict(dict)

	for key1, value1 in combined.items():
		for key2, value2 in value1.items():
			outdict[key2].update({key1: value2})

	return(outdict)
