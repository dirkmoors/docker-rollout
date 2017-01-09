import sys
import dockercloud
import json
import time
from random import shuffle

class TimeoutError(RuntimeError):
    pass


# Message handler for docker-cloud "execute" commands
def msg_handler(output_handler, message):
    try:
        msg_data = json.loads(message)
    except:
        output_handler(message)
    else:
        output_handler(msg_data.get('output', '').strip())


def set_namespace(namespace):
    # Set namespace
    dockercloud.namespace = namespace


def execute(container_uuid, command, output_handler=None):
    # Set default output handler
    output_handler = output_handler or sys.stdout.write

    # Build command
    command = ' '.join(command)
    output_handler('container({container_uuid}): {command}'.format(container_uuid=container_uuid, command=command))

    # Fetch container by id
    container = dockercloud.Container.fetch(container_uuid)

    # Run command against container
    container.execute(command, handler=msg_handler)


def get_service_containers(state, stack, limit, randomize, service):
    if stack:
        result = dockercloud.Container.list(service__name=service, service__stack__name=stack, state=state)
    else:
        result = dockercloud.Container.list(service__name=service, state=state)

    # Shuffle results?
    if randomize:
        shuffle(result)

    # Limit results?
    if limit > 0:
        result = result[:limit]

    return result


def execute_in_stack_service(stack, service, command, output_handler=None):
    # Set default output handler
    output_handler = output_handler or sys.stdout.write

    result = dockercloud.Container.list(service__name=service, service__stack__name=stack, state='Running')

    if not result or len(result) == 0:
        raise dockercloud.ObjectNotFound('No containers running for service {service} in stack {stack}'.format(
            service=service, stack=stack))
    elif len(result) > 1:
        # Shuffle results
        shuffle(result)

    # Take first container in the list
    container = result[0]

    # Build command
    command = ' '.join(command)
    output_handler('container({container_uuid}): {command}'.format(container_uuid=container.uuid, command=command))

    # Run command against container
    container.execute(command, handler=lambda message: msg_handler(output_handler, message))


def redeploy_stack(reuse_volumes, stack):
    result = dockercloud.Stack.list(name=stack)

    if not result or len(result) == 0:
        raise dockercloud.ObjectNotFound('No such stack {stack}'.format(stack=stack))
    elif len(result) > 1:
        raise dockercloud.ObjectNotFound('Multiple stacks found for name {stack}'.format(stack=stack))

    # Tale first (and only) stack
    stack = result[0]

    # Redeploy stack
    stack.redeploy(reuse_volumes=reuse_volumes)


def redeploy_stack_service(reuse_volumes, block, timeout, interval, stack, service, output_handler=None):
    # Set default output handler
    output_handler = output_handler or sys.stdout.write

    result = dockercloud.Service.list(name=service, stack__name=stack)

    if not result or len(result) == 0:
        raise dockercloud.ObjectNotFound('No such service {service} in stack {stack}'.format(
            service=service, stack=stack))

    # Tale first (and only) service
    service = result[0]

    # Redeploy stack
    service.redeploy(reuse_volumes=reuse_volumes)

    # If we're not blocking, just return here
    if not block:
        return

    start = time.time()
    timeout_ms = timeout * 1000
    while True:
        containers = get_service_containers(
            state='Running', stack=stack, limit=-1, randomize=True, service=service.name)
        if len(containers) >= 1 and containers[0].state == 'Running':
            break
        if time.time() - start >= timeout_ms:
            raise TimeoutError('After {timeout}, still no container back in state "Running"!'.format(timeout=timeout))
        output_handler('Waiting for at least 1 container in service {service} to come back to state "Running"'.format(
            service=service.name))
        time.sleep(interval)
