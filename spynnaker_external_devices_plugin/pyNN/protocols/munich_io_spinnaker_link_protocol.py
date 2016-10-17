from enum import Enum

from spinn_front_end_common.utility_models.commands.\
    multi_cast_command_with_payload import \
    MultiCastCommandWithPayload
from spinn_front_end_common.utility_models.commands.\
    multi_cast_command_without_payload import MultiCastCommandWithoutPayload
from spinn_front_end_common.utilities import exceptions
import logging

logger = logging.getLogger(__name__)

# structure of command is IIIIIII-F-DDD

OFFSET_TO_END = 11
OFFSET_TO_I = 4
OFFSET_TO_F = 3
OFFSET_TO_D = 0
OFFSET_FOR_TIMESTAMPS = 29
OFFSET_FOR_RETINA_SIZE = 26
SENSOR_ID_OFFSET = 27

OFFSET_FOR_UART_ID = 2 + SENSOR_ID_OFFSET
PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER = 1

OFFSET_FOR_SENSOR_TIME = 31

# unused parts of protocol
UNUSED_ID_0_DIM_6_KEY = (0 << OFFSET_TO_I) | (6 << OFFSET_TO_D)
UNUSED_ID_6 = (6 << OFFSET_TO_I)
UNUSED_ID_7 = (7 << OFFSET_TO_I)

# command key for setting up the master key of the board
CONFIGURE_MASTER_KEY = (127 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

# command key for setting up what mode of device running on the board
CHANGE_MODE = (127 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

# command for turning off retina output
DISABLE_RETINA_EVENT_STREAMING = (0 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

# command for retina where payload is events
ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION = \
    (0 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

# command for retina where events are the key
ACTIVE_RETINA_EVENT_STREAMING_SET_KEY = (0 << OFFSET_TO_I) | (2 << OFFSET_TO_D)

# set timer / counter for timestamps
SET_TIMER_COUNTER_FOR_TIMESTAMPS = (0 << OFFSET_TO_I) | (3 << OFFSET_TO_D)

# handle master / slave time sync
MASTER_SLAVE_KEY = (0 << OFFSET_TO_I) | (4 << OFFSET_TO_D)

# command for setting bias (whatever the heck that is)
BIAS_KEY = (0 << OFFSET_TO_I) | (5 << OFFSET_TO_D)

# reset retina key.
RESET_RETINA_KEY = (0 << OFFSET_TO_I) | (7 << OFFSET_TO_D)

# request on-board sensor data
SENSOR_REPORTING_OFF_KEY = (1 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

# poll sensors once
POLL_SENSORS_ONCE_KEY = (1 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

# poll sensors continuously
POLL_SENSORS_CONTINUOUSLY_KEY = (1 << OFFSET_TO_I) | (2 << OFFSET_TO_D)

# disable motor
DISABLE_MOTOR_KEY = (2 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

# run motor for total period
MOTOR_RUN_FOR_PERIOD_KEY = (2 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

# raw output for motor 0 (permanent)
MOTOR_0_RAW_PERM_KEY = (2 << OFFSET_TO_I) | (4 << OFFSET_TO_D)

# raw output for motor 1 (permanent)
MOTOR_1_RAW_PERM_KEY = (2 << OFFSET_TO_I) | (5 << OFFSET_TO_D)

# raw output for motor 0 (leak towards 0)
MOTOR_0_RAW_LEAK_KEY = (2 << OFFSET_TO_I) | (6 << OFFSET_TO_D)

# raw output for motor 1 (leak towards 0)
MOTOR_1_RAW_LEAK_KEY = (2 << OFFSET_TO_I) | (7 << OFFSET_TO_D)

# motor output duration timer period
MOTOR_TIMER_A_TOTAL_PERIOD_KEY = (3 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
MOTOR_TIMER_B_TOTAL_PERIOD_KEY = (3 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
MOTOR_TIMER_C_TOTAL_PERIOD_KEY = (3 << OFFSET_TO_I) | (4 << OFFSET_TO_D)

# motor output ratio active period
MOTOR_TIMER_A_CHANNEL_0_ACTIVE_PERIOD_KEY = \
    (4 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
MOTOR_TIMER_A_CHANNEL_1_ACTIVE_PERIOD_KEY = \
    (4 << OFFSET_TO_I) | (1 << OFFSET_TO_D)
MOTOR_TIMER_B_CHANNEL_0_ACTIVE_PERIOD_KEY = \
    (4 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
MOTOR_TIMER_B_CHANNEL_1_ACTIVE_PERIOD_KEY = \
    (4 << OFFSET_TO_I) | (3 << OFFSET_TO_D)
MOTOR_TIMER_C_CHANNEL_0_ACTIVE_PERIOD_KEY = \
    (4 << OFFSET_TO_I) | (4 << OFFSET_TO_D)
MOTOR_TIMER_C_CHANNEL_1_ACTIVE_PERIOD_KEY = \
    (4 << OFFSET_TO_I) | (5 << OFFSET_TO_D)

# digital IO Signals
QUERY_STATES_LINES_KEY = (5 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

# set output pattern to payload
SET_OUTPUT_PATTERN_KEY = (5 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

# add payload (logic or (PL)) to current output
ADD_PAYLOAD_TO_CURRENT_OUTPUT_KEY = (5 << OFFSET_TO_I) | (2 << OFFSET_TO_D)

# remove payload (logic or (PL)) to current output from current output
REMOVE_PAYLOAD_TO_CURRENT_OUTPUT_KEY = (5 << OFFSET_TO_I) | (3 << OFFSET_TO_D)

# set payload pins to high impedance
SET_PAYLOAD_TO_HIGH_IMPEDANCE_KEY = (5 << OFFSET_TO_I) | (4 << OFFSET_TO_D)

# set laser params for push bot
PUSH_BOT_LASER_CONFIG_TOTAL_PERIOD = (4 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
PUSH_BOT_LASER_CONFIG_ACTIVE_TIME = (5 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
PUSH_BOT_LASER_FREQUENCY = (37 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

# set led params for push bot
PUSH_BOT_LED_CONFIG_TOTAL_PERIOD = (4 << OFFSET_TO_I) | (4 << OFFSET_TO_D)
PUSH_BOT_LED_BACK_CONFIG_ACTIVE_TIME = (5 << OFFSET_TO_I) | (4 << OFFSET_TO_D)
PUSH_BOT_LED_FRONT_CONFIG_ACTIVE_TIME = (5 << OFFSET_TO_I) | (5 << OFFSET_TO_D)
PUSH_BOT_LED_FREQUENCY = (37 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

# set speaker params for push bot
PUSH_BOT_SPEAKER_CONFIG_TOTAL_PERIOD = (4 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
PUSH_BOT_SPEAKER_CONFIG_ACTIVE_TIME = (5 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
PUSH_BOT_SPEAKER_TONE_BEEP = (36 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
PUSH_BOT_SPEAKER_TONE_MELODY = (36 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

# push bot motor control
PUSH_BOT_MOTOR_0_PERMANENT_VELOCITY = (32 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
PUSH_BOT_MOTOR_1_PERMANENT_VELOCITY = (32 << OFFSET_TO_I) | (1 << OFFSET_TO_D)
PUSH_BOT_MOTOR_0_LEAKY_VELOCITY = (32 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
PUSH_BOT_MOTOR_1_LEAKY_VELOCITY = (32 << OFFSET_TO_I) | (3 << OFFSET_TO_D)

# payloads for the different modes
PAYLOAD_RESET_TO_DEFAULT_MODE = 0
PAYLOAD_SET_TO_PUSH_BOT_MODE = 1
PAYLOAD_SET_TO_SPOMNI_BOT_MODE = 2
PAYLOAD_SET_TO_BALL_BALANCER_MODE = 3
PAYLOAD_SET_TO_MY_OROBOTICS_PROJECT_MODE = 4
PAYLOAD_SET_TO_FREE_MODE = 5

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


class MunichIoSpiNNakerLinkProtocol(object):
    # types of modes supported by this protocol
    MODES = Enum(
        value="MODES",
        names=[('RESET_TO_DEFAULT', 0),
               ('PUSH_BOT', 1),
               ('SPOMNIBOT', 2),
               ('BALL_BALANCER', 3),
               ('MY_ORO_BOTICS', 4),
               ('FREE', 5)])

    # id for the key for the instance of the protocol.
    protocol_instance = 0

    def __init__(self, mode=None, instance_key=None):
        self._mode = mode
        if instance_key is None:
            self._instance_key = \
                MunichIoSpiNNakerLinkProtocol.\
                protocol_instance << OFFSET_TO_END
            MunichIoSpiNNakerLinkProtocol.protocol_instance += 1
        else:
            self._instance_key = instance_key

    @property
    def instance_key(self):
        return self._instance_key

    def get_configure_master_key_command(self, new_key, time=0):
        return MultiCastCommandWithPayload(
            key=CONFIGURE_MASTER_KEY | self._instance_key, payload=new_key,
            time=time, repeat=0, delay_between_repeats=0)

    def get_set_mode_command(self, time=0):
        if self._mode == self.MODES.PUSH_BOT:
            return MultiCastCommandWithPayload(
                key=CHANGE_MODE | self._instance_key,
                payload=PAYLOAD_SET_TO_PUSH_BOT_MODE, time=time, repeat=0,
                delay_between_repeats=0)
        if self._mode == self.MODES.SPOMNIBOT:
            return MultiCastCommandWithPayload(
                key=CHANGE_MODE | self._instance_key,
                payload=PAYLOAD_SET_TO_SPOMNI_BOT_MODE, time=time, repeat=0,
                delay_between_repeats=0)
        if self._mode == self.MODES.BALL_BALANCER:
            return MultiCastCommandWithPayload(
                key=CHANGE_MODE | self._instance_key,
                payload=PAYLOAD_SET_TO_BALL_BALANCER_MODE, time=time, repeat=0,
                delay_between_repeats=0)
        if self._mode == self.MODES.MY_ORO_BOTICS:
            return MultiCastCommandWithPayload(
                key=CHANGE_MODE | self._instance_key,
                payload=PAYLOAD_SET_TO_MY_OROBOTICS_PROJECT_MODE,
                time=time, repeat=0, delay_between_repeats=0)
        if self._mode == self.MODES.FREE:
            return MultiCastCommandWithPayload(
                key=CHANGE_MODE | self._instance_key,
                payload=PAYLOAD_SET_TO_FREE_MODE,
                time=time, repeat=0, delay_between_repeats=0)
        raise exceptions.ConfigurationException(
            "The mode given is not recognised within this protocol.")

    def set_retina_transmission_key(self, new_key=None, uart_id=0, time=0):
        return MultiCastCommandWithPayload(
            key=(ACTIVE_RETINA_EVENT_STREAMING_SET_KEY |
                 uart_id << OFFSET_FOR_UART_ID | self._instance_key),
            payload=new_key, time=time, repeat=0, delay_between_repeats=0)

    def disable_retina_event_streaming(self, uart_id=0, time=0):
        return MultiCastCommandWithoutPayload(
            key=(DISABLE_RETINA_EVENT_STREAMING |
                 (uart_id << OFFSET_FOR_UART_ID)  | self._instance_key),
            time=time, repeat=0, delay_between_repeats=0)

    def master_slave_use_internal_counter(self, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MASTER_SLAVE_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=PAYLOAD_MASTER_SLAVE_USE_INTERNAL_COUNTER,
            time=time, repeat=0, delay_between_repeats=0)

    def master_slave_set_slave(self, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MASTER_SLAVE_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=PAYLOAD_MASTER_SLAVE_SET_SLAVE,
            time=time, repeat=0, delay_between_repeats=0)

    def master_slave_set_master_clock_not_started(self, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MASTER_SLAVE_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_NOT_STARTED,
            time=time, repeat=0, delay_between_repeats=0)

    def master_slave_set_master_clock_active(self, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MASTER_SLAVE_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_ACTIVE,
            time=time, repeat=0, delay_between_repeats=0)

    def bias_values(self, bias_id, bias_value, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(BIAS_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=((bias_id << 0) | (bias_value << 8)),
            time=time, repeat=0, delay_between_repeats=0)

    def reset_retina(self, uart_id=0, time=0):
        return MultiCastCommandWithoutPayload(
            key=(RESET_RETINA_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            time=time, repeat=0, delay_between_repeats=0)

    def turn_off_sensor_reporting(self, sensor_id, time):
        return MultiCastCommandWithPayload(
            key=SENSOR_REPORTING_OFF_KEY | self._instance_key,
            payload=(sensor_id << SENSOR_ID_OFFSET),
            time=time, repeat=0, delay_between_repeats=0)

    def poll_sensors_once(self, sensor_id, time):
        return MultiCastCommandWithPayload(
            key=POLL_SENSORS_ONCE_KEY | self._instance_key,
            payload=(sensor_id << SENSOR_ID_OFFSET),
            time=time, repeat=0, delay_between_repeats=0)

    def poll_individual_sensor_continuously(self, sensor_id, time, time_in_ms):
        return MultiCastCommandWithPayload(
            key=POLL_SENSORS_CONTINUOUSLY_KEY | self._instance_key,
            payload=((sensor_id << SENSOR_ID_OFFSET) |
                    (time_in_ms << OFFSET_FOR_SENSOR_TIME)),
            time=time, repeat=0, delay_between_repeats=0)

    def generic_motor_enable_disable(self, enable_disable, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(DISABLE_MOTOR_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=enable_disable,
            time=time, repeat=0, delay_between_repeats=0)

    def generic_motor_total_period_duration(self, time_in_ms, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_RUN_FOR_PERIOD_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=time_in_ms,
            time=time, repeat=0, delay_between_repeats=0)

    def generic_motor0_raw_output_permanent(self, pwm_signal, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_0_RAW_PERM_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=pwm_signal, time=time, repeat=0, delay_between_repeats=0)

    def generic_motor1_raw_output_permanent(self, pwm_signal, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_1_RAW_PERM_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=pwm_signal, time=time, repeat=0, delay_between_repeats=0)

    def generic_motor0_raw_output_leak_to_0(self, pwm_signal, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_0_RAW_LEAK_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=pwm_signal, time=time, repeat=0, delay_between_repeats=0)

    def generic_motor1_raw_output_leak_to_0(self, pwm_signal, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_1_RAW_LEAK_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                 self._instance_key),
            payload=pwm_signal, time=time, repeat=0, delay_between_repeats=0)

    def pwm_pin_output_timer_a_duration(self, timer_period, time, uart_id):
        return MultiCastCommandWithPayload(
            key=(MOTOR_TIMER_A_TOTAL_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=timer_period, time=time, repeat=0, delay_between_repeats=0)

    def pwm_pin_output_timer_b_duration(self, timer_period, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_TIMER_B_TOTAL_PERIOD_KEY | self._instance_key |
                 (uart_id << OFFSET_FOR_UART_ID)), payload=timer_period,
            time=time, repeat=0, delay_between_repeats=0)

    def pwm_pin_output_timer_c_duration(self, timer_period, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_TIMER_C_TOTAL_PERIOD_KEY | self._instance_key |
                 (uart_id << OFFSET_FOR_UART_ID)), payload=timer_period,
            time=time, repeat=0, delay_between_repeats=0)

    def pwm_pin_output_timer_a_channel_0_ratio(
            self, timer_period, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_TIMER_A_CHANNEL_0_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=timer_period, time=time, repeat=0,
            delay_between_repeats=0)

    def pwm_pin_output_timer_a_channel_1_ratio(
            self, timer_period, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_TIMER_A_CHANNEL_1_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=timer_period, time=time, repeat=0,
            delay_between_repeats=0)

    def pwm_pin_output_timer_b_channel_0_ratio(
            self, timer_period, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_TIMER_B_CHANNEL_0_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=timer_period, time=time, repeat=0,
            delay_between_repeats=0)

    def pwm_pin_output_timer_b_channel_1_ratio(
            self, timer_period, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_TIMER_B_CHANNEL_1_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=timer_period, time=time, repeat=0,
            delay_between_repeats=0)

    def pwm_pin_output_timer_c_channel_0_ratio(
            self, timer_period, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_TIMER_C_CHANNEL_0_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=timer_period, time=time, repeat=0,
            delay_between_repeats=0)

    def pwm_pin_output_timer_c_channel_1_ratio(
            self, timer_period, time, uart_id=0):
        return MultiCastCommandWithPayload(
            key=(MOTOR_TIMER_C_CHANNEL_1_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=timer_period, time=time, repeat=0,
            delay_between_repeats=0)

    def query_state_of_io_lines(self, time):
        return MultiCastCommandWithoutPayload(
            key=QUERY_STATES_LINES_KEY | self._instance_key, time=time,
            repeat=0, delay_between_repeats=0)

    def set_output_pattern_for_payload(self, payload, time):
        return MultiCastCommandWithPayload(
            key=SET_OUTPUT_PATTERN_KEY | self._instance_key, payload=payload,
            time=time, repeat=0, delay_between_repeats=0)

    def add_payload_logic_to_current_output(self, payload, time):
        return MultiCastCommandWithPayload(
            key=ADD_PAYLOAD_TO_CURRENT_OUTPUT_KEY | self._instance_key,
            payload=payload, time=time, repeat=0, delay_between_repeats=0)

    def remove_payload_logic_to_current_output(self, payload, time):
        return MultiCastCommandWithPayload(
            key=REMOVE_PAYLOAD_TO_CURRENT_OUTPUT_KEY | self._instance_key,
            payload=payload, time=time, repeat=0, delay_between_repeats=0)

    def set_payload_pins_to_high_impedance(self, payload, time):
        return MultiCastCommandWithPayload(
            key=SET_PAYLOAD_TO_HIGH_IMPEDANCE_KEY | self._instance_key,
            payload=payload, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_laser_config_total_period(
            self, total_period, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_LASER_CONFIG_TOTAL_PERIOD |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=total_period, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_laser_config_active_time(self, active_time, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_LASER_CONFIG_ACTIVE_TIME |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=active_time, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_laser_set_frequency(self, frequency, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_LASER_FREQUENCY | self._instance_key |
                 (uart_id << PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER)),
            payload=frequency, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_speaker_config_total_period(
            self, total_period, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_SPEAKER_CONFIG_TOTAL_PERIOD |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=total_period, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_speaker_config_active_time(
            self, active_time, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_SPEAKER_CONFIG_ACTIVE_TIME |
                 (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
            payload=active_time, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_speaker_set_tone(self, frequency, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_SPEAKER_TONE_BEEP | self._instance_key |
                 (uart_id << PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER)),
            payload=frequency, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_speaker_set_melody(self, melody, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_SPEAKER_TONE_MELODY | self._instance_key |
                 (uart_id << PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER)),
            payload=melody, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_led_total_period(self, total_period, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_LED_CONFIG_TOTAL_PERIOD | self._instance_key |
                 (uart_id << OFFSET_FOR_UART_ID)),
            payload=total_period, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_led_back_active_time(self, active_time, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_LED_BACK_CONFIG_ACTIVE_TIME | self._instance_key |
                 (uart_id << OFFSET_FOR_UART_ID)),
            payload=active_time, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_led_front_active_time(self, active_time, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_LED_FRONT_CONFIG_ACTIVE_TIME | self._instance_key |
                 (uart_id << OFFSET_FOR_UART_ID)),
            payload=active_time, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_led_set_frequency(self, frequency, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_LED_FREQUENCY | self._instance_key |
                 (uart_id << PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER)),
            payload=frequency, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_motor_0_permanent(self, velocity, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_MOTOR_0_PERMANENT_VELOCITY | self._instance_key |
                 (uart_id << OFFSET_FOR_UART_ID)),
            payload=velocity, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_motor_1_permanent(self, velocity, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_MOTOR_1_PERMANENT_VELOCITY | self._instance_key |
                 (uart_id << OFFSET_FOR_UART_ID)),
            payload=velocity, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_motor_0_leaking_towards_zero(
            self, velocity, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_MOTOR_0_LEAKY_VELOCITY | self._instance_key |
                 (uart_id << OFFSET_FOR_UART_ID)),
            payload=velocity, time=time, repeat=0, delay_between_repeats=0)

    def push_bot_motor_1_leaking_towards_zero(
            self, velocity, uart_id=0, time=0):
        if self._mode is not self.MODES.PUSH_BOT:
            raise exceptions.ConfigurationException(
                "The mode you configured is not the push bot, and so this "
                "message is invalid for mode {}".format(self._mode))
        return MultiCastCommandWithPayload(
            key=(PUSH_BOT_MOTOR_1_LEAKY_VELOCITY | self._instance_key |
                 (uart_id << OFFSET_FOR_UART_ID)),
            payload=velocity, time=time, repeat=0, delay_between_repeats=0)

    def set_retina_transmission(
            self, events_in_key=True, retina_pixels=128*128,
            payload_holds_time_stamps=False, size_of_time_stamp_in_bytes=None,
            uart_id=0, time=0, repeat=0, delay=0):

        # if events in the key.
        if events_in_key:
            if not payload_holds_time_stamps:
                # not using payloads
                return self._key_retina(
                    retina_pixels, PAYLOAD_NO_TIMESTAMPS, uart_id, time,
                    repeat, delay)
            else:
                # using payloads
                if  size_of_time_stamp_in_bytes == 0:
                    return self._key_retina(
                        retina_pixels, PAYLOAD_DELTA_TIMESTAMPS,
                        uart_id, time, repeat, delay)
                if size_of_time_stamp_in_bytes == 2:
                    return self._key_retina(
                        retina_pixels, PAYLOAD_TWO_BYTE_TIME_STAMPS,
                        uart_id, time, repeat, delay)
                if size_of_time_stamp_in_bytes == 3:
                    return self._key_retina(
                        retina_pixels, PAYLOAD_THREE_BYTE_TIME_STAMPS,
                        uart_id, time, repeat, delay)
                if size_of_time_stamp_in_bytes == 4:
                    return self._key_retina(
                        retina_pixels, PAYLOAD_FOUR_BYTE_TIME_STAMPS,
                        uart_id, time, repeat, delay)
        else:  # using payloads to hold all events

            # warn users about models
            logger.warning(
                "The current SpyNNaker models do not support the reception of"
                " packets with payloads, therefore you will need to add a "
                "adaptor model between the device and spynnaker models.")

            # verify that its what the end user wants.
            if (payload_holds_time_stamps or
                    size_of_time_stamp_in_bytes is not None):
                raise exceptions.ConfigurationException(
                    "If you are using payloads to store events, you cannot"
                    " have time stamps at all.")
            return MultiCastCommandWithPayload(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
                payload=(PAYLOAD_NO_TIMESTAMPS |
                         PAYLOAD_RETINA_NO_DOWN_SAMPLING_IN_PAYLOAD),
                time=time, repeat=repeat, delay_between_repeats=delay)

    def _key_retina(
            self, retina_pixels, time_stamps, uart_id, time, repeat, delay):
        if retina_pixels == 128 * 128:
            return MultiCastCommandWithPayload(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
                payload=(time_stamps | PAYLOAD_RETINA_NO_DOWN_SAMPLING),
                time=time, repeat=repeat, delay_between_repeats=delay)
        if retina_pixels == 64 * 64:
            return MultiCastCommandWithPayload(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
                payload=(time_stamps | PAYLOAD_RETINA_64_DOWN_SAMPLING),
                time=time, repeat=repeat, delay_between_repeats=delay)
        if retina_pixels == 32 * 32:
            return MultiCastCommandWithPayload(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
                payload=(time_stamps | PAYLOAD_RETINA_32_DOWN_SAMPLING),
                time=time, repeat=repeat, delay_between_repeats=delay)
        if retina_pixels == 16 * 16:
            return MultiCastCommandWithPayload(
                key=(ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                     (uart_id << OFFSET_FOR_UART_ID) | self._instance_key),
                payload=(time_stamps | PAYLOAD_RETINA_16_DOWN_SAMPLING),
                time=time, repeat=repeat, delay_between_repeats=delay)
        else:
            raise exceptions.ConfigurationException(
                "The no of pixels is not supported in this protocol.")



