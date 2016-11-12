from enum import Enum
from spynnaker.pyNN import exceptions
import logging
from spinn_front_end_common.utility_models.multi_cast_command import \
    MultiCastCommand

logger = logging.getLogger(__name__)

# types of modes supported by this protocol
MODES = Enum(
    value="MODES",
    names=[('RESET_TO_DEFAULT', 0),
           ('PUSH_BOT', 1),
           ('SPOMNIBOT', 2),
           ('BALL_BALANCER', 3),
           ('MY_ORO_BOTICS', 4),
           ('FREE', 5)])

# structure of command is IIIIIII-F-DDD

OFFSET_TO_I = 4
OFFSET_TO_F = 3
OFFSET_TO_D = 0
OFFSET_FOR_TIMESTAMPS = 0
OFFSET_FOR_RETINA_SIZE = 3
OFFSET_FOR_RETINA_ID = 7

# command key for setting up the master key of the board
CONFIGURE_MASTER_KEY = (127 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

# command key for setting up what mode of device running on the board
CHANGE_MODE = (127 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

# payloads for the different modes
PAYLOAD_RESET_TO_DEFAULT_MODE = 0
PAYLOAD_SET_TO_PUSH_BOT_MODE = 1
PAYLOAD_SET_TO_SPOMNI_BOT_MODE = 2
PAYLOAD_SET_TO_BALL_BALANCER_MODE = 3
PAYLOAD_SET_TO_MY_OROBOTICS_PROJECT_MODE = 4
PAYLOAD_SET_TO_FREE_MODE = 5

# command for turning off retina output
DISABLE_RETINA_EVENT_STREAMING = (0 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

# command for retina where payload is events
ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION = \
    (0 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

# command for retina where events are the key
ACTIVE_RETINA_EVENT_STREAMING_SET_KEY = \
    (0 << OFFSET_TO_I) | (2 << OFFSET_TO_D)

# set timer / counter for timestamps
SET_TIMER_COUNTER_FOR_TIMESTAMPS = \
    (0 << OFFSET_TO_I) | (3 << OFFSET_TO_D)

# handle master / slave time sync
MASTER_SLAVE_KEY = \
    (0 << OFFSET_TO_I) | (4 <<  OFFSET_TO_D)

# payload for setting different time stamp sizes
PAYLOAD_NO_TIMESTAMPS = (0 << OFFSET_FOR_TIMESTAMPS)
PAYLOAD_DELTA_TIMESTAMPS = (1 << OFFSET_FOR_TIMESTAMPS)
PAYLOAD_TWO_BYTE_TIME_STAMPS = (2 << OFFSET_FOR_TIMESTAMPS)
PAYLOAD_THREE_BYTE_TIME_STAMPS = (3 << OFFSET_FOR_TIMESTAMPS)
PAYLOAD_FOUR_BYTE_TIME_STAMPS = (4 << OFFSET_FOR_TIMESTAMPS)

# payload for retina size
PAYLOAD_RETINA_NO_DOWN_SAMPLING_IN_PAYLOAD = (0 << OFFSET_FOR_RETINA_SIZE)
PAYLOAD_RETINA_NO_DOWN_SAMPLING = (1 << OFFSET_FOR_RETINA_SIZE)
PAYLOAD_RETINA_64_DOWN_SAMPLING = (2 << OFFSET_FOR_RETINA_SIZE)
PAYLOAD_RETINA_32_DOWN_SAMPLING = (3 << OFFSET_FOR_RETINA_SIZE)
PAYLOAD_RETINA_16_DOWN_SAMPLING = (4 << OFFSET_FOR_RETINA_SIZE)

# payload for master slave
PAYLOAD_MASTER_SLAVE_USE_INTERNAL_COUNTER = 0
PAYLOAD_MASTER_SLAVE_SET_SLAVE = 1
PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_NOT_STARTED = 2
PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_ACTIVE = 4



class MunichIoProtocol(object):

    def __init__(self, mode=None):
        self._mode = mode

    def get_configure_master_key_command(self, new_key):
        return MultiCastCommand(
                key=CONFIGURE_MASTER_KEY, payload=new_key, time=0,
                repeat=1, delay_between_repeats=100)

    def get_set_mode_command(self):
        if self._mode == MODES.PUSH_BOT:
            return MultiCastCommand(
                key=CHANGE_MODE, payload=PAYLOAD_SET_TO_PUSH_BOT_MODE, time=0,
                repeat=1, delay_between_repeats=100)
        if self._mode == MODES.SPOMNIBOT:
            return MultiCastCommand(
                key=CHANGE_MODE, payload=PAYLOAD_SET_TO_SPOMNI_BOT_MODE,
                time=0, repeat=1, delay_between_repeats=100)
        if self._mode == MODES.BALL_BALANCER:
            return MultiCastCommand(
                key=CHANGE_MODE, payload=PAYLOAD_SET_TO_BALL_BALANCER_MODE,
                time=0, repeat=1, delay_between_repeats=100)
        if self._mode == MODES.MY_ORO_BOTICS:
            return MultiCastCommand(
                key=CHANGE_MODE,
                payload=PAYLOAD_SET_TO_MY_OROBOTICS_PROJECT_MODE,
                time=0, repeat=1, delay_between_repeats=100)
        if self._mode == MODES.FREE:
            return MultiCastCommand(
                key=CHANGE_MODE,
                payload=PAYLOAD_SET_TO_FREE_MODE,
                time=0, repeat=1, delay_between_repeats=100)
        raise exceptions.SynapticConfigurationException(
            "The mode given is not recognised within this protocol.")

    def set_retina_transmission_key(self, new_key):
        return MultiCastCommand(
            key=ACTIVE_RETINA_EVENT_STREAMING_SET_KEY,
            payload=new_key, time=0, repeat=1, delay_between_repeats=100)

    def master_slave_use_internal_counter(self):
        return MultiCastCommand(
            key=MASTER_SLAVE_KEY,
            payload=PAYLOAD_MASTER_SLAVE_USE_INTERNAL_COUNTER,
            time=0, repeat=1, delay_between_repeats=100)

    def master_slave_set_slave(self):
        return MultiCastCommand(
            key=MASTER_SLAVE_KEY,
            payload=PAYLOAD_MASTER_SLAVE_SET_SLAVE,
            time=0, repeat=1, delay_between_repeats=100)

    def master_slave_set_master_clock_not_started(self):
        return MultiCastCommand(
            key=MASTER_SLAVE_KEY,
            payload=PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_NOT_STARTED,
            time=0, repeat=1, delay_between_repeats=100)

    def master_slave_set_master_clock_active(self):
        return MultiCastCommand(
            key=MASTER_SLAVE_KEY,
            payload=PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_ACTIVE,
            time=0, repeat=1, delay_between_repeats=100)

    def bias_values(self, bias_id, bias_value):
        return MultiCastCommand(
            key=,
            payload=,
            time=0, repeat=1, delay_between_repeats=100)

    def set_retina_transmission(
            self, events_in_key=True, retina_pixels=128*128,
            payload_holds_time_stamps=False, size_of_time_stamp_in_bytes=None,
            retina_id=0):

        # shift retina id over to bits 4..3 of id.
        retina_id = (retina_id << OFFSET_FOR_RETINA_ID)

        # if events in the key.
        if events_in_key:
            if not payload_holds_time_stamps:
                # not using payloads
                return self._key_retina(
                    retina_pixels, PAYLOAD_NO_TIMESTAMPS, retina_id)
            else:
                # using payloads
                if  size_of_time_stamp_in_bytes == 0:
                    return self._key_retina(
                        retina_pixels, PAYLOAD_DELTA_TIMESTAMPS, retina_id)
                if size_of_time_stamp_in_bytes == 2:
                    return self._key_retina(
                        retina_pixels, PAYLOAD_TWO_BYTE_TIME_STAMPS, retina_id)
                if size_of_time_stamp_in_bytes == 3:
                    return self._key_retina(
                        retina_pixels, PAYLOAD_THREE_BYTE_TIME_STAMPS,
                        retina_id)
                if size_of_time_stamp_in_bytes == 4:
                    return self._key_retina(
                        retina_pixels, PAYLOAD_FOUR_BYTE_TIME_STAMPS,
                        retina_id)
        else:  # using payloads to hold all events

            # warn users about models
            logger.warning(
                "The current SpyNNaker models do not support the reception of"
                " packets with payloads, therefore you will need to add a "
                "adaptor model between the device and spynnaker models.")

            # verify that its what the end user wants.
            if (payload_holds_time_stamps or
                    size_of_time_stamp_in_bytes is not None):
                raise exceptions.SynapticConfigurationException(
                    "If you are using payloads to store events, you cannot"
                    " have time stamps at all.")
            return MultiCastCommand(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     retina_id),
                payload=(PAYLOAD_NO_TIMESTAMPS |
                         PAYLOAD_RETINA_NO_DOWN_SAMPLING_IN_PAYLOAD),
                time=0, repeat=1, delay_between_repeats=100)

    @staticmethod
    def _key_retina(retina_pixels, time_stamps, retina_id):
        if retina_pixels == 128 * 128:
            return MultiCastCommand(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     retina_id),
                payload=(time_stamps | PAYLOAD_RETINA_NO_DOWN_SAMPLING),
                time=0, repeat=1, delay_between_repeats=100)
        if retina_pixels == 64 * 64:
            return MultiCastCommand(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     retina_id),
                payload=(time_stamps | PAYLOAD_RETINA_64_DOWN_SAMPLING),
                time=0, repeat=1, delay_between_repeats=100)
        if retina_pixels == 32 * 32:
            return MultiCastCommand(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     retina_id),
                payload=(time_stamps | PAYLOAD_RETINA_32_DOWN_SAMPLING),
                time=0, repeat=1, delay_between_repeats=100)
        if retina_pixels == 16 * 16:
            return MultiCastCommand(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     retina_id),
                payload=(time_stamps | PAYLOAD_RETINA_16_DOWN_SAMPLING),
                time=0, repeat=1, delay_between_repeats=100)
        else:
            raise exceptions.SynapticConfigurationException(
                "The no of pixels is not supported in this protocol.")



