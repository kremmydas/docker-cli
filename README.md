# fncli

`fncli` is a command line interface tool for docker engine that can do the following:
 * Build a Docker Image from a given Dockerfile and run a container
 * Start a few instances of the Docker Image in different containers
 * Validate that the container instances are running
 * Monitor the resource usage of each container (CPU, I/O, memory, network)
 * Fetch logs of containers and stream logs real-time
 * Consolidate the log output of all the container instances into one centralized log file.

 You can see the list of commands and features below.

 ![usage](/data/2019-01-29_19:22:24.png)

## Installing in virtualenv and running ##

```
$ git clone https://github.com/andreask81/docker-cli.git
$ cd docker-cli
$ virtualenv venv
$ source venv/bin/activate
(venv)$ pip install --editable .
(venv)$ pip install -r requirements.txt
(venv)$ fncli
```

## [Bash completion](https://click.palletsprojects.com/en/7.x/bashcomplete/) ##

  Run the following:
  ```
  (venv)$ _FNCLI_COMPLETE=source fncli > fncli-complete.sh
  ```
  And then add this into your .bashrc file: ```. /path/to/fncli-complete.sh```

## Built With ##
* [Python](https://www.python.org/)
* [Click](https://click.palletsprojects.com/en/7.x/)
* [Docker SDK](https://docker-py.readthedocs.io/en/stable/)
