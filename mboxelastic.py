#!/usr/bin/env python3
import sys
import json
import argparse
import logging

import jwzthreading as th

import perceval.backends
import elasticsearch

import logging

import argparse

msg_ids = []
msg_json = []


# ElasticSearch instance (url)
es = elasticsearch.Elasticsearch(['http://localhost:9200/'])

es.indices.create('thm')
res = es.search(index="mboxes")

print("%d documents found" % res['hits']['total'])
for doc in res['hits']['hits']:
    print("%s) %s" % (doc['_id'], doc['_source'])

messages = th.message_details(res, file)
for key, value in messages.items():
    for k in msg_json:
        try:
            if key == k['data']['Message-ID'].strip('<>'):
                k['property'] = key
                summary = {'message': mboxes['data']['Message-ID']}
            
            	# Upload the object to ElasticSearch
            	es.index(index='thm', doc_type='summary', body=summary)
                break
        except KeyError:
                logging.debug('Received an email without the correct Message Id %s', str(k))

    if value:
        for i in value:
            for j in msg_json:
                try:
                    if i == j['data']['Message-ID'].strip('<>'):
                        j['property'] = key
                        summary = {'message': mboxes['data']['Message-ID']}
            
            			# Upload the object to ElasticSearch
            			es.index(index='thm', doc_type='summary', body=summary)
                        break
                except KeyError as e:
                        logging.debug('Received an email without the correct Message Id')
