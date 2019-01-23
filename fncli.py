from __future__ import division
import click
import docker
import os.path
from six.moves import input
import pandas as pd
import json
from pandas.io.json import json_normalize
from dateutil.parser import parse
from hurry.filesize import size, si


client = docker.from_env()

pd.set_option('display.expand_frame_repr', False)

@click.group()
def cli():
    """A simple command line tool for docker engine."""
    pass

@click.command()
def status():
    """Get the status and attributes of containers. """

    try:
        headers = ('CONTAINER ID', 'IMAGE', 'NAME', 'COMMAND', 'STATUS', 'CREATED')
        column_width=30
        for el in headers:
            print(el.ljust(column_width)),
        print('')

        for container in client.containers.list(True):
            column_width=30
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
def stats(name):
    """Monitor the resource usage of a container."""

    try:
        column_width=25
        container = client.containers.get(name)
        stats = container.stats(stream=False)

        blkio = stats.get('blkio_stats').get('io_service_bytes_recursive')
        # blkio_read = size(blkio[0].get('value'), system=si) # IndexError: list index out of range
        # blkio_write = size(blkio[1].get('value'), system=si) # IndexError: list index out of range
        blkio_read = 'test'
        blkio_write = 'test'
        rx = size(stats.get('networks').get('eth0').get('rx_bytes'), system=si)
        tx = size(stats.get('networks').get('eth0').get('tx_bytes'), system=si)

        mem = stats.get('memory_stats')
        mem_usage = mem.get('stats').get('active_anon')
        mem_limit = mem.get('limit')
        mem_percent = ("%.2f"%((mem_usage / mem_limit)*100))

        # this is taken directly from docker client:
        #   https://github.com/docker/docker/blob/28a7577a029780e4533faf3d057ec9f6c7a10948/api/client/stats.go#L309
        cpu_percent = 0.0
        cpu = stats.get('cpu_stats')
        pre_cpu = stats.get('precpu_stats')
        cpu_total = cpu.get('cpu_usage').get('total_usage')
        pre_cpu_total = pre_cpu.get('cpu_usage').get('total_usage')
        cpu_count = cpu.get('online_cpus')

        cpu_delta = cpu_total - pre_cpu_total
        system_delta = cpu.get('system_cpu_usage') - pre_cpu.get('system_cpu_usage')

        if system_delta > 0.0 and cpu_delta > 0.0:
            cpu_percent = ("%.2f"%(cpu_delta / system_delta * 100.0 * cpu_count))

        attrs = [('CONTAINER ID', 'NAME', 'CPU %', 'MEM USAGE / LIMIT', 'MEM %', 'NET I/O', 'BLOCK I/O', 'PIDS'), (str(container.short_id), str(container.name), str(cpu_percent), str(size((mem_usage),system=si) + " / " + size((mem_limit),system=si)), str(mem_percent), str(rx + " / " + tx), str(blkio_read + " / " + blkio_write), str(stats.get('pids_stats').get('current')))]
        for row in attrs:
            for element in row:
                print(element.ljust(column_width)),
            print('')
    except docker.errors.NotFound as e:
        print(e)

    except (docker.errors.NotFound, KeyError) as e:
        print('No such container or container not running!')

@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name')
def top(name):
    """Similar to docker top command."""

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
@click.option('--dockerfile', help='The full path of Dockerfile, e.g fncli create ./Dockerfile')
@click.argument('dockerfile')
def create(dockerfile):
    """Build a Docker Image from a Dockerfile and run an application."""

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
