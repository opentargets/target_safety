import argparse
import json
from helpers import *

def get_high_expression_in_safety_tissues(expression_index):
	# jejunum not available,replaced by small intestine. eye is under sense organ
	#original_safety_tissues = ['adrenal','colon','eye','heart','small intestine',
	#                  'kidney','liver','lung','ovaries','testes','thymus','brain'] #
	# thymus hasn't been assigned to an organ/tissue (probably immune organ? alt. immune system/lymphoid system?),
	# so it doesn't appear, even though we have data
	safety_organs = ['endocrine gland','exocrine gland','intestine','sense organ',
					 'heart','kidney','lung','reproductive organ','immune organ','brain']
	safety_express = {}
	with open(expression_index ) as expressionfile:
		for line in expressionfile:
			gene_entry = json.loads(line)
			#gene_entry = json.loads(line)['_source']
			ensembl_id = gene_entry['gene']
			tissues = gene_entry['tissues']
			for tissue in tissues:
				organs = tissue['organs']
				if any(org in safety_organs for org in organs):
					if tissue['rna']['level']==3:
						safety_express.setdefault(ensembl_id, {}).setdefault('Bucket_T1:high_expression_in_safety_organs',set()).update([o for o in organs if o in safety_organs])
					elif any(cell['level']==3 for cell in tissue['protein']['cell_type']):
						safety_express.setdefault(ensembl_id, {}).setdefault('Bucket_T1:high_expression_in_safety_organs',set()).update([o for o in organs if o in safety_organs])
			if ensembl_id in safety_express:
				safety_express[ensembl_id]['Bucket_T1:high_expression_in_safety_organs'] = list(safety_express[ensembl_id]['Bucket_T1:high_expression_in_safety_organs'])

	return(safety_express)

def get_high_expression_in_safety_tissues_backup(expression_index):
	# alternative more specific, probably need to add more tissues
	safety_tissues = ['adrenal gland','colon','eye','heart','small intestine',
					  'kidney','liver','lung','ovary','testis','thymus','brain']
	safety_express = {}
	with open(expression_index ) as expressionfile:
		for line in expressionfile:
			gene_entry = json.loads(line)
			#gene_entry = json.loads(line)['_source']
			ensembl_id = gene_entry['gene']
			tissues = gene_entry['tissues']
			for tissue in tissues:
				if tissue['label'] in safety_tissues:
					if tissue['rna']['level']==3:
						safety_express.setdefault(ensembl_id, {}).setdefault('Bucket_T1:high_expression_in_safety_organs',[]).append(tissue['label'])
					elif any(cell['level']==3 for cell in tissue['protein']['cell_type']):
						safety_express.setdefault(ensembl_id, {}).setdefault('Bucket_T1:high_expression_in_safety_organs',[]).append(tissue['label'])

	return(safety_express)

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-expression_index", help="Open Targets gene expression index contents", required=True)
	parser.add_argument("-o", "--output", help="Output json filename", required=True)
	args = parser.parse_args()

	high_tissue_expression = get_high_expression_in_safety_tissues(args.expression_index)
	write_json_file(high_tissue_expression,args.output)
