from helpers import *
import argparse

def get_paralogues(paralogue_file):

	high_perc_paralogues = {}
	with open (paralogue_file,'r') as parfile:
		#header = next(parfile)
		for line in parfile:
			line = line.split()
			high_perc = (float(line[3]) >= 80 or float(line[4]) >= 80)

			if high_perc:
				high_perc_paralogues.setdefault(line[0],{'Bucket_O1:high_perc_paralogues':[]})['Bucket_O1:high_perc_paralogues'].append({'paralogue':line[1],'paralogue_type':line[2],'paral_perc_id':line[3], 'query_perc_id': line[4]})
				#high_perc_paralogues.setdefault(line[0],[]).append({'paralogue':line[1],'paralogue_type':line[2],'paral_perc_id':line[3], 'query_perc_id': line[4]})
	return(high_perc_paralogues)

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Ensembl human paralogues tsv filename")
	parser.add_argument("-o", "--output", help="Output json filename")
	args = parser.parse_args()

	high_perc_paralogues = get_paralogues(args.input)
	write_json_file(high_perc_paralogues,args.output)
