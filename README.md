# What do to with this?

Firstly, pull containernet/containernet image from docker. Then run it in one terminal with command:
`sudo docker run --name containernet --rm -it --privileged --pid='host' -v /var/run/docker.sock:/var/run/docker.sock containernet/containernet /bin/bash`

After that open second terminal and run `./script.sh` script. This will build redis-server and client images. Also it will
copy required files to containernet container and attaches to it. As you'll be inside containernet container, execute `containernet.py` python script by typing `sudo python3 containernet.py`. It SHOULD end with creating containernet cli but if not, there's something wrong with configuration. When you see containernet cli, open another terminal and execute `copy_results.sh` script to download results to your machine.

## Configuration
```json
{
    "type": "single_instance",
    "instances": [
        {
            "host": "10.0.0.10",
            "cpu": 100
        }
    ],
    "benchmark_script": "benchmark.py",
    "metrics": [
        "used_memory",
        "evicted_keys"
    ]
}
```

Where:
* type - redis configuration type (for now only "single_instance" is supported).
* instances - list of redis hosts with cpu quota (for now only one redis host is allowed).
* benchmark_script - script with `benchmark(client: redis)` function that will be invoked to perform your benchmark.
* metrics - list of redis metrics you want to write to `result.csv` file.

Please, notice, that if you change benchmark script to some other script, you need to copy this new file in Dockerfile.app dockerfile, so our script performing your benchmark will be able to import it.