import argparse
import requests

def download_GoogleSpreadSheet(gkey,gid,output_filename):

    # downloads provided Google Spreadsheet into a file in tsv format

    uri = "https://docs.google.com/spreadsheets/d/{}/export?format=tsv&gid={}".format(gkey,gid)
    response = requests.get(uri)
    with open(output_filename, mode='wb') as localfile:
        localfile.write(response.content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-gkey", help="Google spreadsheet key", required=True)
    parser.add_argument("-gid", help="Google spreadsheet gid", required=True)
    parser.add_argument("-o", "--output", help="Output filename", required=True)
    args = parser.parse_args()

    download_GoogleSpreadSheet(args.gkey,args.gid,args.output)
