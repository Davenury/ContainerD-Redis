import redis
import sys

def main():

    r = redis.Redis(host='localhost', port=6379)

    # perform scenario on r

    r.set('key', 1)
    r.get('key')

    # get info
    info = r.info()

    interesting_metrics = {}

    metrics = sys.argv[2:]
    cpu = sys.argv[1]
    
    row = [f"{info.get(metric, None)}" for metric in metrics]
    row.append(cpu)

    with open('result.csv', 'a+') as f:
        f.write(','.join(row))
        f.write('\n')

if __name__ == '__main__':
    main()