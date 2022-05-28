# What do to with this?

Firstly, pull containernet/containernet image from docker. Then run it in one terminal with command:
`sudo docker run --name containernet --rm -it --privileged --pid='host' -v /var/run/docker.sock:/var/run/docker.sock containernet/containernet /bin/bash`

After that open second terminal and run `./script.sh` script. This will build redis-server and client images. Also it will
copy required files to containernet container and attaches to it. As you'll be inside containernet container, execute `example.py` (TODO: change this name) python script by typing `sudo python3 example.py`. It SHOULD end with creating containernet cli but if not, there's something wrong with configuration. When you see containernet cli, open another terminal and execute `copy_results.sh` script to download results to your machine.

## Configuration
Well, not so fast. It's still TODO. (Probably some kinds of configs files - one for client app for metrics and another one for containernet file).