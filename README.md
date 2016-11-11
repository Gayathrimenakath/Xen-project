# Xen Code Review Dashboard project

A python based project incorporating Perceval, Elasticsearch and Kibana. The project is to feed the data of Xen-devel mailing list to Elasticsearch database.

mboxes of the Xen-devel mailing list are fetched using Perceval.
eg: python3 mboxparser.py --mbox http://lists.xenproject.org/archives/html/mbox/xen-devel-2016-03 --output new.json

The fetched data is feeded to Elasticsearch database.
eg: python perceval_elasticparse.py --mbox http://lists.xenproject.org/archives/html/mbox/xen-devel-2016-03

A dashboard for the data has to be produced using Kibana.
