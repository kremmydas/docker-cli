'''
    File name: fncli.py
    A simple CLI tool for Docker Engine
'''

from __future__ import division
import os.path
import click
import docker
from six.moves import input
import pandas as pd
from dateutil.parser import parse
from hurry.filesize import size, si

CLIENT = docker.from_env()

@click.group()
def cli():
    """A simple command line tool for docker engine."""
    pass


def get_container_name(ctx, args, incomplete):
    """Bash completion"""

    names = [container.name for container in CLIENT.containers.list()]
    c_dict = dict(enumerate(names))
    return [k for k in c_dict.values() if incomplete in k]


@click.command()
def index():
    """Show running containers."""

    try:
        headers = ('CONTAINER ID', 'IMAGE', 'COMMAND', 'STATUS', 'CREATED',
                   'HOST IP / PORT', 'NAMES')
        column_width = 30
        for element in headers:
            print(element.ljust(column_width)),
        print('')

        for container in CLIENT.containers.list():
            column_width = 30

            # Get host port binding
            portbind = container.attrs.get('HostConfig').get('PortBindings')
            if not portbind:
                port = 'None'
            else:
                iter_port = iter(portbind.values())
                port = next(iter_port)[0].get('HostPort')

            # Get host IP
            ports = container.attrs.get('NetworkSettings').get('Ports')
            for c_port in ports.values():
                if c_port is not None:
                    hostip = (c_port)[0].get('HostIp')

            # Get Command
            path = container.attrs.get('Path')
            args = container.attrs.get('Args')
            command_arg = str(path) + " " + str(args[0])

            # container attributes
            attrs = [(str(container.short_id), str(container.attrs.get('Config').get('Image')),
                      command_arg, container.attrs.get('State').get('Status'),
                      str(parse(container.attrs.get('Created')).ctime()),
                      str(hostip + ':' + port), str(container.name))]

            for row in attrs:
                for element in row:
                    print(element.ljust(column_width)),
                print('')

    except docker.errors.NotFound as err:
        print(err)


@click.command()
def watch():
    """Monitor the resource usage of containers."""

    try:
        headers = ('CONTAINER ID', 'NAME', 'CPU %', 'MEM USAGE / LIMIT',
                   'MEM %', 'NET I/O', 'BLOCK I/O', 'PIDS')
        column_width = 20
        for element in headers:
            print(element.ljust(column_width)),
        print('')

        for container in CLIENT.containers.list():
            column_width = 20
            stats = container.stats(stream=False)

            # Block I/O stats
            blkio = stats.get('blkio_stats').get('io_service_bytes_recursive')
            # in case blkio is empty --> IndexError: list index out of range
            if not blkio:
                blkio_read = '0'
                blkio_write = '0'
            else:
                blkio_read = size(blkio[0].get('value'), system=si)
                blkio_write = size(blkio[1].get('value'), system=si)

            # Network stats
            rx_stats = size(stats.get('networks').get('eth0').get('rx_bytes'), system=si)
            tx_stats = size(stats.get('networks').get('eth0').get('tx_bytes'), system=si)

            # Memory stats
            mem = stats.get('memory_stats')
            mem_usage = mem.get('stats').get('active_anon')
            mem_limit = mem.get('limit')
            mem_percent = ("%.2f"%((mem_usage / mem_limit)*100))

            # CPU stats
            # this is taken directly from docker CLIENT:
            # https://github.com/docker/docker/blob/28a7577a029780e4533faf3d057ec9f6c7a10948/api/CLIENT/stats.go#L309
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

            # container attributes
            attrs = [(str(container.short_id), str(container.name), str(cpu_percent),
                      str(size((mem_usage), system=si) + " / " + size((mem_limit), system=si)),
                      str(mem_percent), str(rx_stats + " / " + tx_stats),
                      str(blkio_read + " / " + blkio_write),
                      str(stats.get('pids_stats').get('current')))]

            for row in attrs:
                for element in row:
                    print(element.ljust(column_width)),
                print('')

    except (docker.errors.NotFound, KeyError, AttributeError):
        print('No such container or container not running!')


@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name', type=click.STRING, autocompletion=get_container_name)
def logs(name):
    """Fetch the logs of a container."""

    try:
        container = CLIENT.containers.get(name)
        click.secho(str(container.logs()), bg='blue', fg='white')
    except docker.errors.NotFound as err:
        print(err)


@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name', type=click.STRING, autocompletion=get_container_name)
def tail(name):
    """Follow log output in real-time."""

    try:
        container = CLIENT.containers.get(name)
        for line in container.logs(stream=True):
            click.secho(line.strip(), bg='blue', fg='white')
    except docker.errors.NotFound as err:
        print(err)


@click.command()
@click.option('--name', help='The name of a running container')
@click.argument('name', type=click.STRING, autocompletion=get_container_name)
def top(name):
    """Similar to docker top command."""

    try:
        container = CLIENT.containers.get(name)
        print(str(pd.DataFrame(data=container.top()['Processes'],
                               columns=container.top()['Titles'])))
    except (docker.errors.NotFound, docker.errors.APIError) as err:
        print(err)


@click.command()
def mix():
    """Consolidate the log output of container instances into one centralized log file."""

    with open("output.log", 'w') as outfile:
        log_file = [container.logs(timestamps=True).split(",") for container in
                    CLIENT.containers.list()]
        for c_log in log_file:
            outfile.write(" ".join(map(str, c_log)) + '\n')
        click.secho('Log output of each container has been written to output.log.',
                    bg='blue', fg='white')


@click.command()
@click.option('--dockerfile', help='The full path of Dockerfile, e.g fncli create ./Dockerfile')
@click.argument('dockerfile')
def create(dockerfile):
    """Build a Docker Image from a Dockerfile and run an application."""

    path = os.path.dirname(dockerfile)

    container_name = input('Enter container name: ')
    port = input('Enter port number to map TCP port 5000 in the container, to a port on the Docker host: ')

    try:
        image = CLIENT.images.build(path=path, dockerfile=dockerfile, tag="my_app_image")
        # Run a container and map TCP port 5000 in the container to a given port on the Docker host.
        container = CLIENT.containers.run('my_app_image', detach=True, ports={'5000/tcp': port},
                                          name=container_name)
        click.secho("Container created with name: {}. App is running "
                    "on http://0.0.0.0:{}/ on the host."
                    .format(container_name, port), bg='blue', fg='white')
    except (docker.errors.APIError, TypeError, OSError) as err:
        print(err)


# List of commands
cli.add_command(create)
cli.add_command(index)
cli.add_command(logs)
cli.add_command(mix)
cli.add_command(tail)
cli.add_command(top)
cli.add_command(watch)
