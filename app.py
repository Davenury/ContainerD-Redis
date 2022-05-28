import redis

client = redis.from_url("redis://10.0.0.10:6379")

client.set('key', 1)
client.get('key')

# get info
info = client.info()

interesting_metrics = {}

cpu = '100'
metrics=['used_memory']

row = [f"{info.get(metric, None)}" for metric in metrics]
row.append(cpu)

with open('result.csv', 'a+') as f:
    f.write(','.join(row))
    f.write('\n')