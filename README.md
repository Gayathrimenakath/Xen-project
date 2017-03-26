# Xen Code Review Dashboard project

A python based project incorporating Perceval, Elasticsearch and Kibana. The project is to feed the data of Xen-devel mailing list to Elasticsearch database.

mboxes of the Xen-devel mailing list are fetched using Perceval. A threading algorithm is run over the retrieved data to group the messages belonging to the same thread.
eg: python3 mbox.py --mbox http://lists.xenproject.org/archives/html/mbox/xen-devel-2016-03 --output new.json

The threaded data is feeded to Elasticsearch database.
eg: python perceval_elasticparse.py --filename new.json --indexname mboxes

A search can be performed by giving the field name and the expected value.
python3 search.py --field Sender --result wei.w.wang@intel.com --indexname mboxes


A dashboard for the data has to be produced using Kibana.
