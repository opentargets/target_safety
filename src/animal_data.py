import argparse
import json
from helpers import *

def collect_animal_data(gene_index):
	mouse_phenotypes = {}
	ortholog = {}
	clinical_species = ['human','mouse','pig','dog','macaque','rat','guinea pig','rabbit','chimpanzee'] # TODO: update this
	with open(gene_index) as genefile:
		for line in genefile:
			annot = json.loads(line)
			#annot = json.loads(line)['_source']
			ensembl_id = annot['ensembl_gene_id']
			orth_annot = [an for an in annot['ortholog'] if an in clinical_species]
			if orth_annot != []:
				ortholog[ensembl_id] = orth_annot
			#mp_annot = annot['mouse_phenotypes']
			mp_annot = [an['mouse_gene_id'] for an in annot['mouse_phenotypes']]
			if mp_annot != []:
				mouse_phenotypes[ensembl_id] = mp_annot
	return(mouse_phenotypes,ortholog)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-gene_index", help="Open Targets gene index contents", required=True)
	parser.add_argument("-o", "--output", help="Output json filename", required=True)
	args = parser.parse_args()

	mouse_phenotypes,ortholog = collect_animal_data(args.gene_index)

	combined = {'Info_A1:mouse_models': mouse_phenotypes,'Info_A2:ortholog_for_clinical_species': ortholog}
	animal_data = combine_dicts_genekey(combined)
	#print(disease_assoc_buckets)

	write_json_file(animal_data,args.output)
