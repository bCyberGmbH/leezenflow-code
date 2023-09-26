"""This global state is filled from message data, and used by Animation."""

import time
from leezenflow.message_types import MessageContentParsed
from typing import Optional

global_traffic_light_data: Optional[MessageContentParsed] = None
last_message_timestamp = time.monotonic()

# current_phase = None
disable_display = False
