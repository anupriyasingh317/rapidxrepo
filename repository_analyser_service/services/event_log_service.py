import os
import json
import traceback
from datetime import datetime, UTC
import logging

_LOGGER = logging.getLogger(__name__)

def log_event(sender_cb, run_id, parent_id, level, event_type, message, start_date=None, end_date=None):
    if start_date is None:
        start_date = datetime.now(UTC).isoformat()
    if end_date is None:
        end_date = datetime.now(UTC).isoformat()

    event_data = {
        "code_analysis_run_id": run_id,
        "parent_id": parent_id,
        "level": level,
        "event_type": event_type,
        "message": message,
        "start_date": start_date,
        "end_date": end_date
    }

    sender_cb(
        queue_name=os.environ["EVENT_LOG_QUEUE_NAME"],
        message_body=json.dumps(event_data)
)

def log_error_event(sender_cb, run_id, parent_id, level, event_type, module_name, error: Exception, start_date):
    end_date = datetime.now(UTC).isoformat()
    tb_str = "".join(traceback.format_tb(error.__traceback__))
    message = f"Error in {module_name}. Message: {error}, trace: {tb_str}"
    _LOGGER.error(message)
    log_event(sender_cb, run_id, parent_id, level, event_type, message, start_date, end_date)

def log_skipped_error_event(sender_cb, run_id, parent_id, level, event_type, module_name, error: Exception, start_date):

    end_date = datetime.now(UTC).isoformat()
    tb_str = "".join(traceback.format_tb(error.__traceback__))
    message = f"Skipped Error in {module_name}. Message: {error}, trace: {tb_str}"
    _LOGGER.error(message)
    log_event(sender_cb, run_id, parent_id, level, event_type, message, start_date, end_date)