import click

import logic
from plugins import newrelic


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
        state=state, stack=stack, limit=limit, randomize=randomize, service=service)
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
@click.option('--newrelic_api_key', default=None, type=str)
@click.option('--newrelic_app_id', default=None, type=str)
@click.option('--newrelic_app_revision', default=None, type=str)
@click.option('--newrelic_user', default=None, type=str)
@click.argument('stack')
@click.argument('service')
def redeploy_stack_service(
        reuse_volumes, block, timeout, interval, newrelic_api_key, newrelic_app_id, newrelic_app_revision,
        newrelic_user, stack, service):
    try:
        logic.redeploy_stack_service(
            reuse_volumes=reuse_volumes, block=block, timeout=timeout, interval=interval, stack=stack, service=service,
            output_handler=click.echo)
    except Exception as e:
        click.echo(str(e))
    else:
        newrelic.notify_deployment(
            api_key=newrelic_api_key, app_id=newrelic_app_id, app_revision=newrelic_app_revision, user=newrelic_user,
            output_handler=click.echo)


# Main
if __name__ == '__main__':
    cli()