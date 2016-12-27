#!/usr/bin/env python3
import sys
import json
import argparse
import logging

import jwzthreading as th
import perceval.backends as backend


msg_ids = []
msg_json = []


class MboxParser:

    def getmbox(self, mbox_files):
        mbox_parser = backend.mbox.MBox(
                uri = mbox_files,
                dirpath='./mboxes'
        )
        return mbox_parser.fetch()

    def create_json(self, mbox_files, output_file, file=False):
        percevalout = self.getmbox(mbox_files)
        message_id = ''
        for item in percevalout:
            message_id = item['data']['Message-ID']
            with open(output_file,'a') as f:
                json.dump(item, f, ensure_ascii=True, indent=4)
                
        messages = th.message_details(mbox_files, file)
        with open(output_file,'a') as f:
            for key, value in messages.items():
                for k in msg_json:
                    try:
                        if key == k['data']['Message-ID'].strip('<>'):
                            k['property'] = key
                            json.dump(k, f, ensure_ascii=True, indent=4)
                            break
                    except KeyError:
                            logging.debug('Received an email without the correct Message Id %s', str(k))

                if value:
                    for i in value:
                        for j in msg_json:
                            try:
                                if i == j['data']['Message-ID'].strip('<>'):
                                    j['property'] = key
                                    json.dump(j, f, ensure_ascii=True, indent=4)
                                    break
                            except KeyError as e:
                                logging.debug('Received an email without the correct Message Id')

            f.close()


        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mbox",required=True,help="Give the name of the mbox file to be parsed")
    parser.add_argument("--output", required=True, help="Name of the output json file")
    args = parser.parse_args()
    logging.basicConfig(filename='perceval_mbox_parse.log', level=logging.DEBUG)
    mparser = MboxParser()
    mparser.create_json(args.mbox,args.output)
    print("Output file %s created"%args.output)

if __name__ == "__main__":
    main()


