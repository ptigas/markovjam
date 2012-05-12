import redis

redis = redis.StrictRedis(host='localhost', port=6379, db=0)

nodes = open('nodes.txt', 'r')
for node in nodes :
	node = int(node.rstrip())
	redis.sadd('nodes', node)