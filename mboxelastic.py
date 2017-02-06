#!/usr/bin/env python3
import sys
import json
import argparse
import logging

import jwzthreading as th

from jwzthreading import Container
container = Container()

import perceval.backends
import elasticsearch

import logging

import argparse

msg_ids = []
msg_json = []
messages = []


# ElasticSearch instance (url)
es = elasticsearch.Elasticsearch(['http://localhost:9200/'])

class ElasticThread:

    def threading(self, oldindex, newindex,output_file, file=False):

        es.indices.create(newindex)
        res = es.search(index=oldindex)

        print("%d documents found" % res['hits']['total'])
        for doc in res['hits']['hits']:
            #print("%s) %s" % (doc['_id'], doc['_source'])
            #message_id = doc['data']['Message-ID']
            with open(output_file,'a') as f:
                json.dump(doc, f, ensure_ascii=True, indent=4)

        messages = th.message_details(output_file, file=True)
        #es.index(index='thm', doc_type='summary', body=summary)

        


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--oldindex",required=True,help="Give the name of the index to be searched")
    parser.add_argument("--newindex", required=True, help="Name of the Elasticsearch index to be created")
    parser.add_argument("--output_file",required=True,help="Give the name of the index to be searched")
    args = parser.parse_args()
    logging.basicConfig(filename='perceval_mbox_parse.log', level=logging.DEBUG)
    mparser = ElasticThread()
    mparser.threading(args.oldindex, args.newindex, args.output_file)

if __name__ == "__main__":
    main()

