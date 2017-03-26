# Xen Code Review Dashboard project

A python based project incorporating Perceval, Elasticsearch and Kibana. The project is to feed the data of Xen-devel mailing list to Elasticsearch database.

mboxes of the Xen-devel mailing list are fetched using Perceval. A threading algorithm is run over the retrieved data to group the messages belonging to the same thread.
eg: python3 mbox.py --mbox "url of the archive" --output "JSON file name"

The threaded data is feeded to Elasticsearch database.
eg: python perceval_elasticparse.py --filename "JSON file name" --indexname "indexname"

A search can be performed by giving the field name and the expected value.
python3 search.py --field "Field" --result "Field value" --indexname "indexname"


A dashboard for the data has to be produced using Kibana.
