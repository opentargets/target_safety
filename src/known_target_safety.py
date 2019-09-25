import argparse
import json
from helpers import *

def generate_known_safety_json(filename_adr,filename_sri,filename_ubr,filename_efo,filename_ref):

    # Reference info
    ref_links = {}
    with open(filename_ref) as ref:
        # assert next(ref).strip() == "Reference\tPMID\tOther link\tShort description"
        next(ref)

        for line in ref:
            line = line.split("\t")
            ref_links[line[0].upper().strip()] = {"pmid": line[1].strip(), "link": line[2].strip()}

    # UBERON organ/system mapping
    uberon_map = {}
    with open(filename_ubr) as uberon:
        # assert next(uberon).strip() == "Publication term\tUBERON term\tUBERON code\tUBERON url"
        next(uberon)

        for line in uberon:
            line = line.split("\t")
            uberon_map[line[0].upper().strip()] = {"term": line[1].strip(), "code": line[2].strip()}

    # EFO adverse effect mapping
    efo_map = {}
    with open(filename_efo) as efo:
        # assert next(efo).strip() == "Source term\tOntology term\tCode\tUrl"
        next(efo)

        for line in efo:
            line = line.split("\t")
            efo_map[line[0].upper().strip()] = {"term": line[1].strip(), "code": line[2].strip()}


    # Function for filling in terms and their mapping in the required format
    def make_term_list(terms, mapping):
        term_list = []
        for term in terms:
            term = term.strip()
            mapped_term = ""
            code = ""
            if term.upper() in mapping:
                mapped_term = mapping[term.upper().strip()]["term"]
                code = mapping[term.upper()]["code"]
            term_list.append({
                "term_in_paper": term,
                "mapped_term": mapped_term,
                "code": code})
        return (term_list)

    # Function for generating the references list in the required format
    def make_ref_obj(reflist, ref_links):
        references = []
        for ref in reflist:
            references.append({
                "ref_label": ref,
                "pmid": ref_links[ref.upper()]["pmid"],
                "ref_link": ref_links[ref.upper()]["link"]})
        return (references)


    targets = {}

    # Fill in Adverse Effect information
    with open(filename_adr, "r") as adrs:
        # assert next(adrs).strip() == "Ref\tTarget\tMain organ/system affected\tUnspecified mechanism effects_General\tAgonism/Activation effects_Acute dosing\tAgonism/Activation effects_Chronic dosing\tAgonism/Activation effects_Developmental toxicity\tAgonism/Activation effects_General\tAntagonism/Inhibition effects_Acute dosing\tAntagonism/Inhibition effects_Chronic dosing\tAntagonism/Inhibition effects_Developmental toxicity\tAntagonism/Inhibition effects_General"
        next(adrs)

        for line in adrs:
            line = line.split("\t")
            target = line[1].strip()

            if target not in targets:
                targets[target] = {}

            if "adverse_effects" not in targets[target]:
                targets[target]["adverse_effects"] = []

            inner = {}
            reflist = [x.strip() for x in line[0].split(";") if x]
            organs = [x.strip() for x in line[2].split(";") if x]
            unspec_effects = [x.strip() for x in line[3].split(";") if x]
            act_acute = [x.strip() for x in line[4].split(";") if x]
            act_chr = [x.strip() for x in line[5].split(";") if x]
            act_dev = [x.strip() for x in line[6].split(";") if x]
            act_gen = [x.strip() for x in line[7].split(";") if x]
            inh_acute = [x.strip() for x in line[8].split(";") if x]
            inh_chr = [x.strip() for x in line[9].split(";") if x]
            inh_dev = [x.strip() for x in line[10].split(";") if x]
            inh_gen = [x.strip() for x in line[11].split(";") if x]
            if inh_gen == [""]: inh_gen = []

            inner["references"] = make_ref_obj(reflist, ref_links)

            inner["organs_systems_affected"] = make_term_list(organs, uberon_map)

            inner["unspecified_interaction_effects"] = make_term_list(unspec_effects, efo_map)

            inner["activation_effects"] = {}
            if act_acute:
                inner["activation_effects"]["acute_dosing"] = make_term_list(act_acute, efo_map)
            if act_chr:
                inner["activation_effects"]["chronic_dosing"] = make_term_list(act_chr, efo_map)
            if act_dev:
                inner["activation_effects"]["developmental"] = make_term_list(act_dev, efo_map)
            if act_gen:
                inner["activation_effects"]["general"] = make_term_list(act_gen, efo_map)

            inner["inhibition_effects"] = {}
            if inh_acute:
                inner["inhibition_effects"]["acute_dosing"] = make_term_list(inh_acute, efo_map)
            if inh_chr:
                inner["inhibition_effects"]["chronic_dosing"] = make_term_list(inh_chr, efo_map)
            if inh_dev:
                inner["inhibition_effects"]["developmental"] = make_term_list(inh_dev, efo_map)
            if inh_gen:
                inner["inhibition_effects"]["general"] = make_term_list(inh_gen, efo_map)

            targets[target]["adverse_effects"].append(inner)

    # Fill in Safety risk information
    with open(filename_sri, "r") as riskinfo:
        # assert next(riskinfo).strip() == "Reference\tTarget\tMain organ/system affected\tSafety liability"
        next(riskinfo)

        for line in riskinfo:
            line = line.split("\t")
            target = line[1].strip()

            if target not in targets:
                targets[target] = {}

            if "safety_risk_info" not in targets[target]:
                targets[target]["safety_risk_info"] = []

            inner = {}
            reflist = [x.strip() for x in line[0].split(";") if x]
            inner["references"] = make_ref_obj(reflist, ref_links)

            organs = [x.strip() for x in line[2].split(";")]
            inner["organs_systems_affected"] = make_term_list(organs, uberon_map)
            inner["safety_liability"] = line[3].strip()

            targets[target]["safety_risk_info"].append(inner)

    return(targets)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-adr","--adverse_effects", help="tsv of manually curated adverse effects per target", required=True)
    parser.add_argument("-sri","--safety_risk_info", help="tsv of manually curated safety risk information per target", required=True)
    parser.add_argument("-ubr","--uberon_mapping", help="tsv with uberon mapping for tissues in adverse effect and safety info spreadsheets", required=True)
    parser.add_argument("-efo","--efo_mapping", help="tsv with efo mapping for terms in adverse effect spreadsheet", required=True)
    parser.add_argument("-ref","--references", help="tsv with reference information for entries in adverse effect and safety info spreadsheets", required=True)
    parser.add_argument("-o","--output", help="Output json filename", required=True)
    args = parser.parse_args()
    print(args)

    known_safety_per_target = generate_known_safety_json(args.adverse_effects,args.safety_risk_info,args.uberon_mapping,args.efo_mapping,args.references)
    write_json_file(known_safety_per_target,args.output)
