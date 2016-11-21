import perceval.backends
import elasticsearch

import logging

import argparse

msg_ids = []
msg_json = []


# ElasticSearch instance (url)
es = elasticsearch.Elasticsearch(['http://localhost:9200/'])

res = es.search(index="mboxes")
print("%d documents found" % res['hits']['total'])
for doc in res['hits']['hits']:
    print("%s) %s" % (doc['_id'], doc['_source'])