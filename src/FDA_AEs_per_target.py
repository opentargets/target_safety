import argparse
import json
import pandas as pd
from helpers import *

def make_dict_by_target(x):
	x = x.drop(['target_id'],axis=1).sort_values(by=['llr'],ascending=False).to_json(orient='records')
	return(json.loads(x))

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input", help="significant openFDA adverse events PER TARGET", required=True)
	parser.add_argument("-o","--output", help="Output json filename", required=True)
	args = parser.parse_args()

	aes_df = pd.read_csv(args.input)
	AEs_per_target = aes_df.groupby(['target_id']).apply(make_dict_by_target).to_dict()
	write_json_file(AEs_per_target,args.output)
