def read_json_file(json_file):

	import json

	with open(json_file) as injson:
		data = json.load(injson)

	return(data)


def write_json_file(data,json_file):

	import json

	with open(json_file, 'w') as f:
		json.dump(data, f,indent=4)
		#json.dump(data, f)

def Ensembl_from_HGNC(mapfile):

	import json

	hgnc_to_ensembl = {}
	with open(mapfile) as map:
		for line in map:
			line = json.loads(line)
			hgnc_to_ensembl[line['hgnc_approved_symbol']] = line['ensembl_id']

	return(hgnc_to_ensembl)

def get_EFO_names(disease_mapfile):

	import json

	EFO_names = {}
	with open(disease_mapfile) as map:
		for line in map:
			line = json.loads(line)
			EFO_names[line['efo_id']] = line['disease_full_name']

	return(EFO_names)

# use if map file not available?
def switch_to_EnsemblIDs(mydict, gene_index, type = 'from_symbols'):
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

	# e.g. combined = {'drug_label_info': drug_label_info,'known_target_safety': known_target_safety,...}

	from collections import defaultdict

	outdict = defaultdict(dict)

	for key1, value1 in combined.items():
		for key2, value2 in value1.items():
			outdict[key2].update({key1: value2})

	return(outdict)
