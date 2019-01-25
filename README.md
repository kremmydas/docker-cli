# fncli

`fncli` is a command line interface tool for docker engine that can do the following:
 * Build a Docker Image from a given Dockerfile and run a container
 * Start a few instances of the Docker Image in different containers
 * Validate that the container instances are running
 * Monitor the resource usage of each container (CPU, I/O, memory, network)
 * Fetch logs of containers and stream logs real-time
 * Consolidate the log output of all the container instances into one centralized log file.

 You can see the list of commands and features below.

 ![usage](/data/out.gif)

## Installation in dev environment and running ##

```
$ git clone https://github.com/andreask81/docker-cli.git
$ cd docker-cli
$ virtualenv venv
$ source venv/bin/activate
$ pip install --editable .
$ pip install -r requirements.txt
$ fncli
```

## Notes ##
* In order to run the `cat`command (consolidate the log output to a centralized log file),
you must run `fncli` with sudo permission.
  Before that, you must also run the following pip install commands with sudo:
  * sudo pip install --editable .
  * sudo pip install click docker pandas hurry.filesize

    Otherwise, if you run `fncli` without sudo permission, you receive an IOError error: [Errno 13] Permission denied `u'/var/lib/docker/containers/e37acce2575...-json.log'`

* `fncli` has been written in Python (using the Click package and Docker SDK for Python).

* Bash completion:
  Add the following into your .bashrc: eval "$(_FNCLI_COMPLETE=source fncli)" 
