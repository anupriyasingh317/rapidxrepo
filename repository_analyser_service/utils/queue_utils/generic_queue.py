import threading
from proton import  Delivery, Event, Message, Receiver, SSLDomain, Sender
from proton.handlers import MessagingHandler, Reject
from proton.reactor import Container as ProtonContainer
import json
import os
import logging

_LOGGER = logging.getLogger(__name__)

proton_logger = logging.getLogger("proton")
proton_logger.setLevel(logging.INFO)

from utils.exceptions.UnProcessableMessageException import UnProcessableMessageError


class GenericQueueHandler(MessagingHandler):
    def __init__(self, url, listener_queue, callback, **kwargs):
        super(GenericQueueHandler, self).__init__(prefetch=1, auto_accept=False, auto_settle=False)
        self.url = url
        # self.user = user
        # self.password = password
        self.listener_queue = listener_queue
        self.callback = callback
        self.lock = threading.Lock()
        self.senders = {}

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def on_start(self, event):
        _LOGGER.info(f"listening on {self.url}")
        self.container = event.container
        domain = SSLDomain(SSLDomain.MODE_CLIENT)
        domain.set_peer_authentication(SSLDomain.ANONYMOUS_PEER)
        self.conn = event.container.connect(
            url=self.url,
            ssl_domain=domain,
            heartbeat=20,
            allow_insecure_mechs=True,
            sasl_enabled=True,
            allowed_mechs='PLAIN'
        )
        # self.conn = event.container.connect(self.url, ssl_domain=domain, user=self.username, password=self.password)

    def __get_message_body(self, message_body: str, delivery_count: int) -> str:
        return json.dumps({
            "delivery_count": delivery_count,
            "body": message_body
        })
    
    def __send_message(self, queue_name, message_body: str, delivery_count: int):
        _LOGGER.info(f"sending message {queue_name} - {message_body}")
        body = self.__get_message_body(message_body, delivery_count)
        with self.lock:  # Acquire the lock
            if queue_name not in self.senders:
                self.senders[queue_name] = self.container.create_sender(self.conn, queue_name)
            sender: Sender = self.senders[queue_name]  # Access the sender within the locked section
            sender.send(Message(body))
    
    def __send_batch_message(self, queue_name, message_body: list, delivery_count: int):
        _LOGGER.info(f"sending messages {queue_name}")
        message_bodies = [self.__get_message_body(message, delivery_count)  for message in message_body]
        with self.lock:  # Acquire the lock
            if queue_name not in self.senders:
                self.senders[queue_name] = self.container.create_sender(self.conn, queue_name)
            sender: Sender = self.senders[queue_name]  # Access the sender within the locked section
            for message_body in message_bodies:
                sender.send(Message(message_body))


    def send_messages(self, queue_name, message_body: str | list, delivery_count: int = 0):
        if isinstance(message_body, str):
            self.__send_message(queue_name, message_body, delivery_count)
        elif isinstance(message_body, list):
            self.__send_batch_message(queue_name, message_body, delivery_count)

    def on_connection_opened(self, event: Event):
        self.receiver = event.container.create_receiver(self.conn, self.listener_queue)
        
    
    def consume_message(self):
        ProtonContainer(self).run()
    
    def decode_message(self, message: Message):
        body = message.body
        if not isinstance(body, str):
            body = body.tobytes().decode('utf-8')
        return json.loads(body)
    
    def process_message(self, event: Event):
        delivery = event.delivery
        decoded_message = self.decode_message(event.message)
        _LOGGER.info(f"Received Body {decoded_message}")
        
        delivery_count = decoded_message.get('delivery_count')
        message_body = decoded_message.get('body')
        try:
            self.callback(message_body, self.send_messages)
            _LOGGER.info(f"Message Processing Successful.")
            delivery.update(Delivery.ACCEPTED)
        except UnProcessableMessageError:
            _LOGGER.error(f"Message Processing Failed as UnProcessableMessage.")
            delivery.update(Delivery.REJECTED)
        except Exception as e:
            _LOGGER.error(f"Message Processing Failed as {e}")
            delivery_limit = os.getenv("QUEUE_DELIVERY_LIMIT", 3)
            if delivery_count <= delivery_limit:
                self.send_messages(self.listener_queue, message_body, delivery_count+1)
                delivery.update(Delivery.ACCEPTED)
            else:
                delivery.update(Delivery.REJECTED)
        finally:
            delivery.settle()
            self.receiver.flow(1)

    def on_message(self, event: Event):
        thread = threading.Thread(target=self.process_message, name="message_process", args=[event])
        thread.start()
        
    def on_transport_error(self, event):
        _LOGGER.info(f"Transport Error: {event.transport.condition.description}")
        return super().on_transport_error(event)

    def on_link_error(self, event: Event) -> None:
        _LOGGER.error(f"Link Error {event.link.remote_condition.description}")
        return super().on_link_error(event)

    def on_session_error(self, event: Event) -> None:
        _LOGGER.error(f"Session Error")
        return super().on_session_error(event)

    def on_connection_error(self, event: Event) -> None:
        _LOGGER.error(f"Connection Error")
        return super().on_connection_error(event)
    
    def on_disconnected(self, event: Event) -> None:
        _LOGGER.info("Connection Disconnected")
        return super().on_disconnected(event)

