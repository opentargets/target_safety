import argparse
import pandas as pd
from helpers import *

def make_dict_by_target(x):
	x = x.drop(['target_id','critval'],axis=1).sort_values(by=['llr'],ascending=False).to_dict(orient='records')
	return(x)

def get_AEs_per_target(aes_csv):

	# Reformats the csv output from the openFDA_MonteCarlo_target.R script into a json file with ENSEMBL gene ids as keys
	# and sorts the events by the event log-likelihood ratio (llr) in descending order.

	aes_df = pd.read_csv(aes_csv)
	# get critical value and sorted significant events for each target
	critvals = aes_df.drop(['event', 'report_count', 'llr'], axis=1).drop_duplicates().set_index('target_id').to_dict()[
		'critval']
	sorted_events = aes_df.groupby(['target_id']).apply(make_dict_by_target).to_dict()

	# combine into one dictionary
	combined = {'significant_adverse_events': sorted_events, 'critval': critvals}
	AEs_per_target = combine_dicts_genekey(combined)

	return(AEs_per_target)



if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input", help="significant openFDA adverse events PER TARGET", required=True)
	parser.add_argument("-o","--output", help="Output json filename", required=True)
	args = parser.parse_args()

	AEs_per_target = get_AEs_per_target(args.input)
	write_json_file(AEs_per_target,args.output)
