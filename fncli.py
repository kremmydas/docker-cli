import click
import docker
import os.path
from six.moves import input
import json
import pandas as pd

@click.group()
def cli():
    pass

# list command -- Return a list with the IDs of running containers.
@click.command()
def list():
    client = docker.from_env()
    click.secho(str(client.containers.list()), bg='blue', fg='white')

# info command -- Similar to docker info command
@click.command()
def info():
    client = docker.from_env()
    print(json.dumps(client.containers.client.info(), indent=4))

# top command -- Similar to docker top command
@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name')
def top(name):
    client = docker.from_env()

    try:
        container = client.containers.get(name)
        click.secho(str(pd.DataFrame(data=container.top()['Processes'], columns=container.top()['Titles'])), bg='blue', fg='white')
    except docker.errors.NotFound as e:
        print(e)

# name command - Return a list with the Names of running containers.
@click.command()
def name():
    client = docker.from_env()
    for container in client.containers.list():
        click.secho(str(container.name), bg='blue', fg='white')

# logs command -- View the logs of a container in shell.
@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name')
def logs(name):
    client = docker.from_env()

    try:
        container = client.containers.get(name)
        click.secho(str(container.logs()), bg='blue', fg='white')
    except docker.errors.NotFound as e:
        print(e)

# stream command -- Stream logs of a container in shell.
@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name')
def stream(name):
    client = docker.from_env()

    try:
        container = client.containers.get(name)
        for line in container.logs(stream=True):
            click.secho(line.strip(),bg='blue', fg='white')
    except docker.errors.NotFound as e:
        print(e)

# output command -- Consolidate the log output of all the container instances into one centralized log file.
@click.command()
def output():
    client = docker.APIClient(base_url='unix://var/run/docker.sock')
    print("Enter container(s) name, separated by a space:")
    container_list = [str(x) for x in input().split()]

    try:
        with open("output.log", 'w') as output:
            for container in container_list:
                inspect = client.inspect_container(container)
                extract_key = { k:v for k,v in inspect.items() if 'LogPath' in k }
                extract_filename = extract_key.get('LogPath')
                with open(extract_filename,'rb') as com:
                    output.write(str(com.read())+ "\n")
            click.secho('output.log file generated', bg='blue', fg='white')
    except docker.errors.NotFound as e:
        print(e)

# stats command -- Monitor the resource usage of each container (CPU, memory, network).
@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name')
def stats(name):
    json_key={}
    client = docker.from_env()

    try:
        container = client.containers.get(name)
        stats = container.stats(stream=False)
        # print(json.dumps(container.stats(stream=False), indent=4))
        json_key['cpu_usage'] = stats.get('cpu_stats')
        json_key['memory_stats'] = stats.get('memory_stats')
        json_key['network_stats'] = stats.get('networks')
        print(json.dumps(json_key, indent=4))
    except docker.errors.NotFound as e:
        print(e)

# filter command -- Validate that the container instance is running by entering its Name and returning its ID.
# Returns an empty list if the container is not running.
@click.command()
def filter():
    client = docker.from_env()
    print("Enter container name:")
    container_name = input()
    click.secho(str(client.containers.list(filters={"name":container_name})), bg='blue', fg='white')

# create command -- Build a Docker Image from a given Dockerfile and an application.
# Start a few instances of the Docker Image in different containers
@click.command()
@click.option('--dockerfile', help='The full path of Dockerfile, e.g fncli create ./Dockerfile')
@click.argument('dockerfile')
def create(dockerfile):
    client = docker.from_env()
    path = os.path.dirname(dockerfile)

    print("Enter container name:")
    container_name = input()
    print("Enter port between 5000 - 7000:")
    port = input()

    try:
        image = client.images.build(path=path, dockerfile=dockerfile, tag="my_app_image")
        container = client.containers.run('my_app_image', detach=True, ports={'5000/tcp': port}, name=container_name)
        click.secho('Container created with name: {}. App is running on http://0.0.0.0:{}/ on the host.'.format(container_name, port), bg='blue', fg='white')
    except (docker.errors.APIError, TypeError, OSError) as e:
        print(e)

# List of commands
cli.add_command(create)
cli.add_command(filter)
cli.add_command(info)
cli.add_command(list)
cli.add_command(logs)
cli.add_command(name)
cli.add_command(output)
cli.add_command(stats)
cli.add_command(stream)
cli.add_command(top)
