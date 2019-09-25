import argparse
import json
import re

def get_orphanet_xrefs(efo_obo_file):
	orphanet = []
	with open(efo_obo_file,'r') as obofile:
		start_term=False
		line = obofile.readline()
		while line!='':
			if line.strip() == '[Term]':
				start_term = True
				orphanet_id = ''
				efo_id = ''
				obsolete=False
				line = obofile.readline()
				while start_term==True:
					line = line.strip()
					if line.strip().startswith('id:'):
						efo_id = line.split()[-1]
					if line.strip() == 'is_obsolete: true':
						obsolete=True
					if obsolete:
						if line.startswith('replaced_by:'):
							efo_id = line.split('/')[-1]
					if orphanet_id == '' and line.startswith('xref:'):
						search_term = re.search('(Orphanet:[0-9]+)',line)
						if search_term:
							orphanet_id = search_term.group()
					line = obofile.readline()
					if line.strip() == '':
						start_term = False
				if orphanet_id != '':
					orphanet.append(efo_id)
			line = obofile.readline()
	orphanet = [term.replace(':','_') for term in orphanet]
	return(orphanet)


def collect_rare_diseases(associations_file,orphanet):

	with open(associations_file) as infile:
		rare_diseases = set()
		for line in infile:
			entry = json.loads(line)
			disease = entry['disease']['id']
			eva_somatic = entry['evidence_count']['datasources']['eva_somatic']
			genomics_england = entry['evidence_count']['datasources']['genomics_england']
			if (eva_somatic > 0 or genomics_england > 0) and disease in orphanet:
				rare_diseases.add(disease)

	return(list(rare_diseases))



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-OT_associations", help="Open Targets associations filename.", required=True)
	parser.add_argument("-efo","--efo_obo", help="Latest release of EFO in OBO format.", required=True)
	parser.add_argument("-o","--output", help="Output text filename", required=True)
	args = parser.parse_args()

	orphanet = get_orphanet_xrefs(args.efo_obo)
	rare_diseases = collect_rare_diseases(args.OT_associations, orphanet)

	with open(args.output, 'w') as outfile:
		outfile.write('\n'.join(sorted(rare_diseases)))
