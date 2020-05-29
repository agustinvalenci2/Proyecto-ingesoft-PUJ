from cassandra.cluster import Cluster
cluster=None
session=None
def connect():
	global cluster,session
	cluster = Cluster(["127.0.0.1"], port=9042)
	session=cluster.connect()
	session.execute("use proyecto")

def query(q):
	return session.execute(q)
