import redis
import json

SINGLE_INSTANCE = "single_instance"
INSTANCES_KEY = "instances"
BENCHMARK_SCRIPT = "benchmark_script"

def read_config():
    with open("config.json", "r") as f:
        return json.load(f)


def get_redis_hosts(config):
    redis_hosts = config.get(INSTANCES_KEY, None)
    if redis_hosts is None or len(redis_hosts) == 0:
        raise ValueError('You didn\'t provide instance array in config or instance array length is 0.')
    
    return redis_hosts


def create_single_instance_redis(config):
    redis_host = get_redis_hosts(config)[0].get("host", None)
    return redis.from_url(f"redis://{redis_host}:6379")


def create_redis_client(config):
    redis_type = config.get("type", SINGLE_INSTANCE)

    if redis_type == SINGLE_INSTANCE:
        return create_single_instance_redis(config)
    
    raise ValueError(f"Type {redis_type} is not supported.")


def execute_benchmark(config, client):
    module_path = config.get(BENCHMARK_SCRIPT, None)
    if module_path is None:
        # TODO - think of default benchmark
        raise ValueError(f"You didn't provide {BENCHMARK_SCRIPT} key in config file!")

    try:
        module = __import__(module_path.replace(".py", ""))
    except ImportError:
        raise ValueError(f"Cannot import {module_path.replace('.py', '')} module. Did you copy it in Dockerfile.app?")

    module.benchmark(client)


def write_metrics(config, client):
    info = client.info()

    # TODO - how to handle more hosts with different CPUs?
    cpu = get_redis_hosts(config)[0]["cpu"]
    metrics = config.get("metrics", ["used_memory"])

    row = [f"{info.get(metric, None)}" for metric in metrics]
    row.append(str(cpu))

    with open('result.csv', 'a+') as f:
        f.write(','.join(row))
        f.write('\n')


config = read_config()

client = create_redis_client(config)

execute_benchmark(config, client)

write_metrics(config, client)
