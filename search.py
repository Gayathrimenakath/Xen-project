#!/usr/bin/env python3
import logging
import argparse
import json
import elasticsearch


es = elasticsearch.Elasticsearch(['http://localhost:9200/'])


class Search:

	def query(self, field, result, indexname):
		#search for the particular field and value
		es_result = es.search(index=indexname, doc_type='summary',
                    body={"query": {"match": {field : result}}})

		print("Found %d messages" % es_result['hits']['total'])
		# Print number of messages retrieved
		for message in es_result['hits']['hits']:
			print("Sender: %s\nfrom:  %s\n    Subject: %s" %
        (message['_source']['Sender'], message['_source']['From'], message['_source']['message']))



def main():
 	parser = argparse.ArgumentParser()
 	parser.add_argument("--field",required=True,help="Give the name of the field")
 	parser.add_argument("--result",required=True,help="Give the data to be searched")
 	parser.add_argument("--indexname", required=True, help="Name of the Elasticsearch index")
 	args = parser.parse_args()
 	logging.basicConfig(filename='perceval_mbox_parse.log', level=logging.DEBUG)
 	mparser = Search()
 	mparser.query(args.field,args.result, args.indexname)

if __name__ == "__main__":
    main()
