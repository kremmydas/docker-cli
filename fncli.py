import click
import docker
import os.path
from six.moves import input
import pandas as pd
import json
from pandas.io.json import json_normalize
from dateutil.parser import parse

pd.set_option('display.expand_frame_repr', False)

@click.group()
def cli():
    """A simple command line tool for docker engine."""
    pass

@click.command()
def status():
    """Get the status and attributes of containers. """

    client = docker.from_env()

    try:
        headers = ('CONTAINER ID', 'IMAGE', 'NAME', 'COMMAND', 'STATUS', 'CREATED')
        column_width=25
        for el in headers:
            print(el.ljust(column_width)),
        print('')

        for container in client.containers.list(True):
            column_width=25
            attrs = [(str(container.short_id), str(container.attrs.get('Config').get('Image')),  str(container.name), str(container.attrs.get('Config').get('Cmd')), container.attrs.get('State').get('Status'), str(parse(container.attrs.get('Created'))))]
            for row in attrs:
                for element in row:
                    print(element.ljust(column_width)),
                print('')
    except docker.errors.NotFound as e:
        print(e)

@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name')
def top(name):
    """Similar to docker top command."""

    client = docker.from_env()

    try:
        container = client.containers.get(name)
        print(str(pd.DataFrame(data=container.top()['Processes'], columns=container.top()['Titles'])))
    except (docker.errors.NotFound, docker.errors.APIError) as e:
        print(e)

@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name')
def logs(name):
    """Fetch the logs of a container."""

    client = docker.from_env()

    try:
        container = client.containers.get(name)
        click.secho(str(container.logs()), bg='blue', fg='white')
    except docker.errors.NotFound as e:
        print(e)

@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name')
def follow(name):
    """Follow log output in real-time."""

    client = docker.from_env()

    try:
        container = client.containers.get(name)
        for line in container.logs(stream=True):
            click.secho(line.strip(),bg='blue', fg='white')
    except docker.errors.NotFound as e:
        print(e)

@click.command()
def output():
    """Consolidate the log output of containers into one centralized log file."""

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
            click.secho('File output.log created.', bg='blue', fg='white')
    except docker.errors.NotFound as e:
        print(e)

@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name')
def stats(name):
    """Monitor the resource usage of a container."""

    json_key={}

    client = docker.from_env()

    try:
        container = client.containers.get(name)
        stats = container.stats(stream=False)
        #stats.keys()

        click.secho(str(json_normalize(stats['networks'])), bg='blue', fg='white')
        click.secho(str(json_normalize(stats['blkio_stats'])), bg='blue', fg='white')
        # click.secho(str(json_normalize(data['cpu_usage'])), bg='blue', fg='white')
        # click.secho(str(json_normalize(data['memory'])), bg='blue', fg='white')

    except (docker.errors.NotFound, KeyError) as e:
        print('No such container or container not running!')

@click.command()
@click.option('--dockerfile', help='The full path of Dockerfile, e.g fncli create ./Dockerfile')
@click.argument('dockerfile')
def create(dockerfile):
    """Build a Docker Image from a Dockerfile and run an application."""

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
cli.add_command(follow)
cli.add_command(logs)
cli.add_command(output)
cli.add_command(stats)
cli.add_command(status)
cli.add_command(top)
