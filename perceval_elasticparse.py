#!/usr/bin/env python3
import logging
import argparse
import json
import elasticsearch

msg_ids = []
msg_json = []


# ElasticSearch instance (url)
es = elasticsearch.Elasticsearch(['http://localhost:9200/'])


# Create a mbox object, pointing to uri, using dir_path for fetching
class MboxElastic:

    def elastic(self, threaded_files, indexname):
        try:
            # Create the 'mboxes' index in ElasticSearch
            es.indices.create(indexname)
        except elasticsearch.exceptions.RequestError:
            print('Index already exisits, remove it before running this script again.')
            exit()
        
        jfile = None
        with open(threaded_files) as f:
            for line in f:
                while True:
                    try:
                        jfile = json.loads(line, strict=False)
                        # Create the object (dictionary) to upload to ElasticSearch
                        for j in jfile:
                            summary = {'message': jfile['data']['Message-ID'],
                       'Sender': jfile['data']['X-Env-Sender'],
                       'From' : jfile['data']['From']
                       }
                        break
                    except ValueError:
                        # Not yet a complete JSON value
                        line += next(f)

                # Upload the object to ElasticSearch
                es.index(index=indexname, doc_type='summary', body=summary)
            f.close()
                
                

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename",required=True,help="Give the name of the threaded file")
    parser.add_argument("--indexname", required=True, help="Name of the Elasticsearch index")
    args = parser.parse_args()
    logging.basicConfig(filename='perceval_mbox_parse.log', level=logging.DEBUG)
    mparser = MboxElastic()
    mparser.elastic(args.filename,args.indexname)

if __name__ == "__main__":
    main()

