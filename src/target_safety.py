import argparse
import json
from helpers import *

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-clinical_findings", help="Target safety clinical_buckets.py output.", required=True)
    parser.add_argument("-tissue_expression", help="Target safety tissue_expression.py output.", required=True)
    parser.add_argument("-bio_function", help="Target safety bio_function_buckets.py output.", required=True)
    parser.add_argument("-disease_associations", help="Target safety disease_associations.py output.", required=True)
    parser.add_argument("-animal_data", help="Target safety animal_data.py output.", required=True)
    parser.add_argument("-potential_off_targets", help="Target safety paralogues.py output.", required=True)
    parser.add_argument("-o","--output", help="Output json filename", required=True)
    args = parser.parse_args()

    clinical_findings = read_json_file(args.clinical_findings)
    high_tissue_expression = read_json_file(args.tissue_expression)
    biological_function = read_json_file(args.bio_function)
    disease_associations = read_json_file(args.disease_associations)
    animal_data = read_json_file(args.animal_data)
    high_perc_paralogues = read_json_file(args.potential_off_targets)

    combined = {'clinical_findings': clinical_findings, 'tissue_expression': high_tissue_expression, 'biological_function': biological_function, 'disease_associations': disease_associations, 'animal_data': animal_data, 'potential_off_targets': high_perc_paralogues}
    safety_buckets = combine_dicts_genekey(combined)
    write_json_file(safety_buckets,args.output)
