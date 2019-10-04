import argparse
import json
from helpers import *

if __name__ == '__main__':

    # Merges the output from the seven different scripts:
    # clinical_buckets.py, tissue_expression.py, essential_genes.py, pathways.py, disease_associations.py, animal_data.py and paralogues.py
    # into a single json that uses ENSEMBL gene ids as keys.

    parser = argparse.ArgumentParser()
    parser.add_argument("-clinical_findings", help="Target safety clinical_buckets.py output.", required=True)
    parser.add_argument("-tissue_expression", help="Target safety tissue_expression.py output.", required=True)
    parser.add_argument("-essential_genes", help="Target safety essential_genes.py output.", required=True)
    parser.add_argument("-pathways", help="Target safety pathways.py output.", required=True)
    parser.add_argument("-disease_associations", help="Target safety disease_associations.py output.", required=True)
    parser.add_argument("-animal_data", help="Target safety animal_data.py output.", required=True)
    parser.add_argument("-potential_off_targets", help="Target safety paralogues.py output.", required=True)
    parser.add_argument("-o","--output", help="Output json filename", required=True)
    args = parser.parse_args()

    clinical_findings = read_json_file(args.clinical_findings)
    high_tissue_expression = read_json_file(args.tissue_expression)
    essential_genes = read_json_file(args.essential_genes)
    pathways = read_json_file(args.pathways)
    disease_associations = read_json_file(args.disease_associations)
    animal_data = read_json_file(args.animal_data)
    high_perc_paralogues = read_json_file(args.potential_off_targets)

    combined = {'clinical_findings': clinical_findings, 'tissue_expression': high_tissue_expression, 'essential_genes': essential_genes, 'pathways': pathways, 'disease_associations': disease_associations, 'animal_data': animal_data, 'potential_off_targets': high_perc_paralogues}
    safety_buckets = combine_dicts_genekey(combined)
    write_json_file(safety_buckets,args.output)
