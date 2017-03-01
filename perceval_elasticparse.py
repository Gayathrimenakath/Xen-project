import perceval.backends as backend
import elasticsearch

import logging

import argparse

msg_ids = []
msg_json = []


# ElasticSearch instance (url)
es = elasticsearch.Elasticsearch(['http://localhost:9200/'])


# Create a mbox object, pointing to uri, using dir_path for fetching
class MboxParser:

    def getmbox(self, mbox_files):
        mbox_parser = backend.mbox.MBox(
                uri = mbox_files,
                dirpath='./mboxes'
        )
        return mbox_parser.fetch()

    def elastic(self, mbox_files, indexname):
        try:
            # Create the 'mboxes' index in ElasticSearch
            es.indices.create(indexname)
        except elasticsearch.exceptions.RequestError:
            print('Index already exisits, remove it before running this script again.')
            exit()
        percevalout = self.getmbox(mbox_files)
        message_id = ''
        # Fetch all mboxes as an iteratoir, and iterate it uploading to ElasticSearch
        for mboxes in percevalout:           
            # Create the object (dictionary) to upload to ElasticSearch
            summary = {'message': mboxes['data']['Message-ID'],
                       'Sender': mboxes['data']['X-Env-Sender'],
                       'subject': mboxes['data']['Subject']}
            print(summary)
            # Upload the object to ElasticSearch
            es.index(index=indexname, doc_type='summary', body=summary)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mbox",required=True,help="Give the name of the mbox file to be parsed")
    parser.add_argument("--indexname", required=True, help="Name of the Elasticsearch index")
    args = parser.parse_args()
    logging.basicConfig(filename='perceval_mbox_parse.log', level=logging.DEBUG)
    mparser = MboxParser()
    mparser.elastic(args.mbox,args.indexname)

if __name__ == "__main__":
    main()

