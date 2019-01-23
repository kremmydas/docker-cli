# fncli

`fncli` is a command line interface tool for docker engine that is able to do the following:
 * Build a Docker Image from a given Dockerfile and run a container
 * Start a few instances of the Docker Image in different containers
 * Validate that the container instances are running
 * Monitor the resource usage of each container (CPU, I/O, memory, network)
 * Fetch logs of containers and stream logs real-time
 * Consolidate the log output of all the container instances into one centralized log file.

 You can see the list of commands.

 ![usage](/data/out.gif)

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
* In order to run the `cat`command (consolidate the log output to a centralized log file),
you must run `fncli` with sudo permission.
  Before that, you must also run the following pip install commands with sudo:
  * sudo pip install --editable .
  * sudo pip install click docker pandas hurry.filesize

    Otherwise, you receive an IOError error: [Errno 13] Permission denied `u'/var/lib/docker/containers/e37acce2575...-json.log'`

* `fncli` has been written in Python (using the Click package and Docker SDK for Python).
