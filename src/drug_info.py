import argparse
import json
import pandas as pd
from helpers import *


# REPLACE WITH ChEMBL black box info when ready
def get_black_box_warning_text(pref_drug_name):

    import requests

    rfda = requests.get('https://api.fda.gov/drug/label.json?search=openfda.generic_name.exact:{}'.format(pref_drug_name))
    if "error" in rfda.json():
        rfda = requests.get('https://api.fda.gov/drug/label.json?search=openfda.substance_name.exact:{}'.format(pref_drug_name))
    if "error" not in rfda.json() and 'boxed_warning' in rfda.json()['results'][0]:
        black_box_text=rfda.json()['results'][0]['boxed_warning']
    else:
        black_box_text=''

    return(black_box_text)

# GET ALL SAFETY RELEVANT INFO FROM DRUG INDEX DATA DUMP
def get_drug_info(drug_index, bbox_text):
    drug_annot = {}
    drugs_per_gene = {}

    with open(drug_index) as drugfile:
        for line in drugfile:
            annot = json.loads(line)
            #annot = json.loads(line)['_source']
            drugid = annot['id']
            # get drugs per gene (DO NOT USE GENE INDEX FOR THIS, FAULTY DATA)
            mech = annot.get('mechanisms_of_action',[])
            targets = []
            for elem in mech:
                comp = elem.get('target_components',[])
                for t in comp:
                    targets.append(t['ensembl'])
            for t in targets:
                if t not in drugs_per_gene:
                    drugs_per_gene[t]=[]
                drugs_per_gene[t].append(drugid)

            # fill in drug annotation dict
            name = annot.get('pref_name','')
            wdrawn = annot.get('withdrawn_flag',False)
            bbox = annot.get('black_box_warning',False)
            mphase = annot.get('max_clinical_trial_phase',0)
            drug_annot[drugid]={'id':drugid,'pref_name':name,'withdrawn_flag':wdrawn,
                                     'black_box_warning':bbox,
                                     'max_clinical_trial_phase':mphase}

            wreason = annot.get('withdrawn_reason','')
            wclass = annot.get('withdrawn_class','')
            wcountry = annot.get('withdrawn_country',[])
            wyear = annot.get('withdrawn_year','')
            drug_annot[drugid]["withdrawn_reason"]= wreason
            drug_annot[drugid]["withdrawn_class"]= wclass
            drug_annot[drugid]["withdrawn_country"]= wcountry
            drug_annot[drugid]["withdrawn_year"]= wyear

            # replace text with Fiona's black box info when ready
            if drug_annot[drugid]['black_box_warning']==True and bbox_text:
                drug_annot[drugid]['black_box_fda'] = get_black_box_warning_text(annot['pref_name'])


        return(drug_annot,drugs_per_gene)


def collect_drug_label_info(drug_index, bbox_text=True):

	drug_annot,drugs_per_gene = get_drug_info(drug_index,bbox_text)

	drug_label_info = {}
	for gene in drugs_per_gene:
		drug_label_info[gene]={}
		drugs = list(set(drugs_per_gene[gene])) # drugs are duplicated if a target affected with more than one mechanism by the same drug
		drug_table = [drug_annot.get(drugid,{}) for drugid in drugs]
		df = pd.DataFrame(drug_table)

		drug_label_info[gene]['Info:drug_phase_freq']=json.loads(df['max_clinical_trial_phase'].
														value_counts().to_json())

		wdrawn = json.loads(df.loc[df.withdrawn_flag == True][['id','pref_name','withdrawn_reason',
															  'withdrawn_class',
															  'withdrawn_country',
															  'withdrawn_year']].
							to_json(orient='records'))
		if len(wdrawn):
			drug_label_info[gene]['Bucket_C1:withdrawn_drugs'] = wdrawn

		bbox = df.loc[df.black_box_warning == True]
		if len(bbox.index):

			if bbox_text:
				# switch with column names for additional info here
				bbox = json.loads(bbox[['id','pref_name','black_box_fda']].to_json(orient='records'))
			else:
				bbox = json.loads(bbox[['id','pref_name']].to_json(orient='records'))

			drug_label_info[gene]['Bucket_C2:black_box_drugs'] = bbox

	#return(drug_label_info,drugs_per_gene)
	return(drug_label_info)


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-drug_index", help="Open Targets drug index contents", required=True)
	parser.add_argument("-o","--output", help="Output json filename", required=True)
	args = parser.parse_args()


	#drug_label_info,drugs_per_gene = collect_drug_label_info(drug_index_dump,bbox_text=False)
	drug_label_info = collect_drug_label_info(args.drug_index,bbox_text=False)
	write_json_file(drug_label_info,args.output)
