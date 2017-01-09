import click

import logic


@click.group()
@click.option('--namespace', envvar='DOCKERCLOUD_NAMESPACE')
def cli(namespace):
    if namespace:
        # Set namespace
        logic.set_namespace(namespace)


@cli.command()
@click.argument('container_uuid')
@click.argument('command', nargs=-1)
def execute(container_uuid, command):
    logic.execute(container_uuid=container_uuid, command=command, output_handler=click.echo)


@cli.command()
@click.option('--state', '-s', default='Running')
@click.option('--stack', '-S')
@click.option('--limit', '-l', default=-1, type=int)
@click.option('--randomize', '-r', default=False, type=bool)
@click.argument('service')
def service_containers(state, stack, limit, randomize, service):
    result = logic.get_service_containers(
        state=state, stack=stack, limit=limit, randomize=randomize, service=service, output_handler=click.echo)
    click.echo('\n'.join([container.uuid for container in result]))


@cli.command()
@click.argument('stack')
@click.argument('service')
@click.argument('command', nargs=-1)
def execute_in_stack_service(stack, service, command):
    logic.execute_in_stack_service(stack=stack, service=service, command=command, output_handler=click.echo)


@cli.command()
@click.option('--reuse_volumes', '-R', default=True, type=bool)
@click.argument('stack')
def redeploy_stack(reuse_volumes, stack):
    logic.redeploy_stack(reuse_volumes=reuse_volumes, stack=stack)


@cli.command()
@click.option('--reuse_volumes', '-R', default=True, type=bool)
@click.option('--block', '-b', default=False, type=bool)
@click.option('--timeout', '-t', default=60, type=int)
@click.option('--interval', '-i', default=5, type=int)
@click.argument('stack')
@click.argument('service')
def redeploy_stack_service(reuse_volumes, block, timeout, interval, stack, service):
    logic.redeploy_stack_service(
        reuse_volumes=reuse_volumes, block=block, timeout=timeout, interval=interval, stack=stack, service=service,
        output_handler=click.echo)


# Main
if __name__ == '__main__':
    cli()