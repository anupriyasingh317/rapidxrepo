from .generic_queue import GenericQueueHandler
from .servicebus_queue import ServiceBusQueueHandler
import os
import sys

def get_queue_handler(queue_handler):
    match queue_handler:
        case 'GENERIC':
            return GenericQueueHandler
        case 'SERVICEBUS':
            return ServiceBusQueueHandler
        case _:
            message = f"{queue_handler} is not supported or invalid"
            raise Exception(message)

def start_consuming(queue_name, callback, **kwargs):
    exit_code = 0
    try:
        queue_handler = os.environ["QUEUE_HANDLER"]
        connection_str = os.environ["QUEUE_CONN_STR"]

        QueueHandler = get_queue_handler(queue_handler)
        with QueueHandler(connection_str, queue_name, callback, **kwargs) as queue_handler:
            queue_handler.consume_message()
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    except Exception as e:
        print(e)
        exit_code = 1
    sys.exit(exit_code)

__all__ = [
    start_consuming
]