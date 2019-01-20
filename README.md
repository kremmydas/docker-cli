# fncli

`fncli` is a command line interface tool for docker engine:
 * it can build a Docker Image from a given Dockerfile and run a container
 * start a few instances of the Docker Image in different containers
 * validate that a container is running (returns an empty list if the container is not running)
 * monitor the resource usage of each container (CPU, memory, network)
 * fetch logs of containers and stream logs real-time
 * consolidate the log output of all the container instances into one centralized log file

 You can see the list of commands.

 ![usage](/data/2019-01-20_18:21:37.png)

## Installation and running ##

```
$ git clone https://github.com/andreask81/docker-cli.git
$ cd docker-cli
$ virtualenv venv
$ source venv/bin/activate
$ pip install --editable .
$ pip install -r requirements.txt
$ fncli
```

## Note ##
* In order to run the `output`command (consolidate the log output to a centralized log file),
you must run `fncli` as sudo.
  Also install with sudo the following packages:
  ** sudo pip install click
  ** sudo pip install docker
Otherwise, you receive an IOError error: [Errno 13] Permission denied
`u'/var/lib/docker/containers/e37acce25759f8e3d3cfad3733f9c6602876f424420a0515264c487d481a4a46/e37acce25759f8e3d3cfad3733f9c6602876f424420a0515264c487d481a4a46-json.log'`

* `fncli` has been written in Python and built in Ubuntu 18.04.
