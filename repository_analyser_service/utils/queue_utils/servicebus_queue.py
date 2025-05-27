import json
import os
from threading import Thread, Event
from azure.servicebus import ServiceBusMessage, ServiceBusReceivedMessage
from azure.servicebus import ServiceBusClient, AutoLockRenewer, ServiceBusMessage
from azure.servicebus.exceptions import ServiceBusError
from azure.servicebus.amqp import AmqpMessageHeader
from datetime import datetime
import time
import logging
from types import GeneratorType

_LOGGER = logging.getLogger(__name__)

from utils.exceptions.UnProcessableMessageException import UnProcessableMessageError
servicebus_logger = logging.getLogger('azure.servicebus')
servicebus_logger.setLevel(logging.INFO)

class ServiceBusQueueHandler:
    def __init__(self, conn_str, receiver_queue_name, callback, **kwargs) -> None:
        self.conn_str = conn_str
        self.receiver_queue_name = receiver_queue_name
        self.callback = callback
        self.client = ServiceBusClient.from_connection_string(conn_str=conn_str)
        self.renew_lock_event = Event()
        self.renew_lock_enabled = kwargs.get("renew_lock_enabled", True)
    
    def __enter__(self):
        # self.renewer = AutoLockRenewer(max_lock_renewal_duration=MESSAGE_LOCK_DURATION, on_lock_renew_failure=self._lock_renew_failed,  max_workers=1)
        self.receiver = self.client.get_queue_receiver(queue_name=self.receiver_queue_name, prefetch_count=1)
        self.receiver.__enter__()
        return self
    
    def __get_message_body(self, message_body: str, delivery_count: int) -> str:
        return json.dumps({
            "delivery_count": delivery_count,
            "body": message_body
        })
    
    def __send_message(self, queue_name, message_body: str | list, delivery_count: int):
        body = self.__get_message_body(message_body, delivery_count)
        _LOGGER.info(f"Sending Message to Queue: {queue_name}")
        with self.client.get_queue_sender(queue_name=queue_name) as sender:
            message = ServiceBusMessage(body)
            sender.send_messages(message)
    
    def __send_batch_message(self, queue_name, messages: list, delivery_count: int):
        with self.client.get_queue_sender(queue_name=queue_name) as sender:
            batch_messages = [sender.create_message_batch()]
            message_pointer = 0
            while message_pointer < len(messages):
                body = self.__get_message_body(messages[message_pointer], delivery_count)
                _LOGGER.info(f"Adding Message {body} to batch")
                try:
                    batch_messages[-1].add_message(
                        ServiceBusMessage(body)
                    )
                    message_pointer += 1
                except ValueError:
                    _LOGGER.info(f"Failed to Add Message {body} to Batch. Creating new batch")
                    batch_messages.append(sender.create_message_batch())

            _LOGGER.info(f"{len(batch_messages)} batches are created. Sending messages to Queue: {queue_name}")
            for message_batch in batch_messages:
                sender.send_messages(message_batch)
    
    def send_messages(self, queue_name, message_body: str | list, delivery_count: int = 0):
        if isinstance(message_body, str):
            self.__send_message(queue_name, message_body, delivery_count)
        elif isinstance(message_body, list):
            self.__send_batch_message(queue_name, message_body, delivery_count)
    
    def renew_lock(self, message: ServiceBusReceivedMessage):
        try:
            while not self.renew_lock_event.is_set():
                # https://github.com/Azure/azure-sdk-for-python/issues/35717
                # fix: https://github.com/Azure/azure-sdk-for-python/pull/35889
                while not self.receiver._handler.client_ready():
                    time.sleep(0.05)
                self.receiver.renew_message_lock(message=message)
                _LOGGER.info(f"Message renewal success for message {message.message_id}")

                self.renew_lock_event.wait(240)
        except Exception as e:
            _LOGGER.info(f"Failed to renew the Message with ID: {message.message_id} as {e}")
    
    def decode_message(self, body):
        if isinstance(body, GeneratorType):
            return bytes().join(body)
        return body
    
    def process_message(self, message: ServiceBusReceivedMessage):
        body = self.decode_message(message.body)
        decoded_body: dict = json.loads(body.decode("utf-8"))
        delivery_count = decoded_body.get('delivery_count')
        message_body = decoded_body.get('body')
        try:
            self.callback(message_body, self.send_messages)
            self.receiver.complete_message(message=message)
        except UnProcessableMessageError:
            self.receiver.dead_letter_message(message=message)
        except Exception as e:
            self.receiver.abandon_message(message=message)

    def consume_message(self):
        while True:
            _LOGGER.info("listening for message")
            received_messages = self.receiver.receive_messages(max_wait_time=30)
            if received_messages:
                message: ServiceBusReceivedMessage = received_messages[0]
                _LOGGER.info(f"Received message: {str(message.body)}, type: {type(message.body)}")

                if self.renew_lock_enabled:
                    renew_lock_thread = Thread(target=self.renew_lock, name=f"renew_lock_{message.message_id}", args=[message])
                    renew_lock_thread.start()

                self.process_message(message=message)

                if self.renew_lock_enabled:
                    self.renew_lock_event.set()     # setting internal flag to stop renew_lock thread
                    renew_lock_thread.join()        # waiting for renew_lock thread to terminate
                    self.renew_lock_event.clear()   # clearing the internal flag for processing for next message
    
    @staticmethod
    def _lock_renew_failed(msg, exception):
        # Maybe we can stop processing the message, if renewal is failed, and update it to appropriate status
        _LOGGER.error(f"Failed to renew message lock. Message: {msg}. Error: {exception}")
            
    
    def close(self):
        self.receiver.close()
        self.client.close()
            
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
