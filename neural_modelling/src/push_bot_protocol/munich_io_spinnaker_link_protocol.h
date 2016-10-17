// structure of command is IIIIIII-F-DDD
#include <debug.h>
#define OFFSET_TO_I 4
#define OFFSET_TO_F 3
#define OFFSET_TO_D 0
#define OFFSET_FOR_TIMESTAMPS 29
#define OFFSET_FOR_RETINA_SIZE 26
#define SENSOR_ID_OFFSET 27

#define OFFSET_FOR_UART_ID 2 + SENSOR_ID_OFFSET
#define PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER 1

#define OFFSET_FOR_SENSOR_TIME 31

// unused parts of protocol
#define UNUSED_ID_0_DIM_6_KEY (0 << OFFSET_TO_I) | (6 << OFFSET_TO_D)
#define UNUSED_ID_6 (6 << OFFSET_TO_I)
#define UNUSED_ID_7 (7 << OFFSET_TO_I)

// command key for setting up the master key of the board
#define CONFIGURE_MASTER_KEY (127 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

// command key for setting up what mode of device running on the board
#define CHANGE_MODE (127 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

// command for turning off retina output
#define DISABLE_RETINA_EVENT_STREAMING \
    (0 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

// command for retina where payload is events
#define ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION \
    (0 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

// command for retina where events are the key
#define ACTIVE_RETINA_EVENT_STREAMING_SET_KEY \
    (0 << OFFSET_TO_I) | (2 << OFFSET_TO_D)

// set timer / counter for timestamps
#define SET_TIMER_COUNTER_FOR_TIMESTAMPS \
    (0 << OFFSET_TO_I) | (3 << OFFSET_TO_D)

// handle master / slave time sync
#define MASTER_SLAVE_KEY (0 << OFFSET_TO_I) | (4 << OFFSET_TO_D)

// command for setting bias (whatever the heck that is)
#define BIAS_KEY (0 << OFFSET_TO_I) | (5 << OFFSET_TO_D)

// reset retina key.
#define RESET_RETINA_KEY (0 << OFFSET_TO_I) | (7 << OFFSET_TO_D)

// request on-board sensor data
#define SENSOR_REPORTING_OFF_KEY (1 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

// poll sensors once
#define POLL_SENSORS_ONCE_KEY (1 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

// poll sensors continuously
#define POLL_SENSORS_CONTINUOUSLY_KEY \
    (1 << OFFSET_TO_I) | (2 << OFFSET_TO_D)

// disable motor
#define DISABLE_MOTOR_KEY (2 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

// run motor for total period
#define MOTOR_RUN_FOR_PERIOD_KEY (2 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

// raw output for motor 0 (permanent)
#define MOTOR_0_RAW_PERM_KEY (2 << OFFSET_TO_I) | (4 << OFFSET_TO_D)

// raw output for motor 1 (permanent)
#define MOTOR_1_RAW_PERM_KEY (2 << OFFSET_TO_I) | (5 << OFFSET_TO_D)

// raw output for motor 0 (leak towards 0)
#define MOTOR_0_RAW_LEAK_KEY (2 << OFFSET_TO_I) | (6 << OFFSET_TO_D)

// raw output for motor 1 (leak towards 0)
#define MOTOR_1_RAW_LEAK_KEY (2 << OFFSET_TO_I) | (7 << OFFSET_TO_D)

// motor output duration timer period
#define MOTOR_TIMER_A_TOTAL_PERIOD_KEY \
    (3 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
#define MOTOR_TIMER_B_TOTAL_PERIOD_KEY \
    (3 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
#define MOTOR_TIMER_C_TOTAL_PERIOD_KEY \
    (3 << OFFSET_TO_I) | (4 << OFFSET_TO_D)

// motor output ratio active period
#define MOTOR_TIMER_A_CHANNEL_0_ACTIVE_PERIOD_KEY \
    (4 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
#define MOTOR_TIMER_A_CHANNEL_1_ACTIVE_PERIOD_KEY \
    (4 << OFFSET_TO_I) | (1 << OFFSET_TO_D)
#define MOTOR_TIMER_B_CHANNEL_0_ACTIVE_PERIOD_KEY \
    (4 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
#define MOTOR_TIMER_B_CHANNEL_1_ACTIVE_PERIOD_KEY \
    (4 << OFFSET_TO_I) | (3 << OFFSET_TO_D)
#define MOTOR_TIMER_C_CHANNEL_0_ACTIVE_PERIOD_KEY \
    (4 << OFFSET_TO_I) | (4 << OFFSET_TO_D)
#define MOTOR_TIMER_C_CHANNEL_1_ACTIVE_PERIOD_KEY \
    (4 << OFFSET_TO_I) | (5 << OFFSET_TO_D)

// digital IO Signals
#define QUERY_STATES_LINES_KEY (5 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

// set output pattern to payload
#define SET_OUTPUT_PATTERN_KEY (5 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

// add payload (logic or (PL)) to current output
#define ADD_PAYLOAD_TO_CURRENT_OUTPUT_KEY \
    (5 << OFFSET_TO_I) | (2 << OFFSET_TO_D)

// remove payload (logic or (PL)) to current output from current output
#define REMOVE_PAYLOAD_TO_CURRENT_OUTPUT_KEY \
    (5 << OFFSET_TO_I) | (3 << OFFSET_TO_D)

// set payload pins to high impedance
#define SET_PAYLOAD_TO_HIGH_IMPEDANCE_KEY \
    (5 << OFFSET_TO_I) | (4 << OFFSET_TO_D)

// set laser params for push bot
#define PUSH_BOT_LASER_CONFIG_TOTAL_PERIOD \
    (4 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
#define PUSH_BOT_LASER_CONFIG_ACTIVE_TIME \
    (5 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
#define PUSH_BOT_LASER_FREQUENCY \
    (37 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

// set led params for push bot
#define PUSH_BOT_LED_CONFIG_TOTAL_PERIOD \
    (4 << OFFSET_TO_I) | (4 << OFFSET_TO_D)
#define PUSH_BOT_LED_BACK_CONFIG_ACTIVE_TIME \
    (5 << OFFSET_TO_I) | (4 << OFFSET_TO_D)
#define PUSH_BOT_LED_FRONT_CONFIG_ACTIVE_TIME \
    (5 << OFFSET_TO_I) | (5 << OFFSET_TO_D)
#define PUSH_BOT_LED_FREQUENCY \
    (37 << OFFSET_TO_I) | (0 << OFFSET_TO_D)

// set speaker params for push bot
#define PUSH_BOT_SPEAKER_CONFIG_TOTAL_PERIOD \
    (4 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
#define PUSH_BOT_SPEAKER_CONFIG_ACTIVE_TIME \
    (5 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
#define PUSH_BOT_SPEAKER_TONE_BEEP \
    (36 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
#define PUSH_BOT_SPEAKER_TONE_MELODY \
    (36 << OFFSET_TO_I) | (1 << OFFSET_TO_D)

// push bot motor control
#define PUSH_BOT_MOTOR_0_PERMANENT_VELOCITY \
    (32 << OFFSET_TO_I) | (0 << OFFSET_TO_D)
#define PUSH_BOT_MOTOR_1_PERMANENT_VELOCITY \
    (32 << OFFSET_TO_I) | (1 << OFFSET_TO_D)
#define PUSH_BOT_MOTOR_0_LEAKY_VELOCITY \
    (32 << OFFSET_TO_I) | (2 << OFFSET_TO_D)
#define PUSH_BOT_MOTOR_1_LEAKY_VELOCITY \
    (32 << OFFSET_TO_I) | (3 << OFFSET_TO_D)

// payloads for the different modes
#define PAYLOAD_RESET_TO_DEFAULT_MODE 0
#define PAYLOAD_SET_TO_PUSH_BOT_MODE 1
#define PAYLOAD_SET_TO_SPOMNI_BOT_MODE 2
#define PAYLOAD_SET_TO_BALL_BALANCER_MODE 3
#define PAYLOAD_SET_TO_MY_OROBOTICS_PROJECT_MODE 4
#define PAYLOAD_SET_TO_FREE_MODE 5

// payload for setting different time stamp sizes
#define PAYLOAD_NO_TIMESTAMPS (0 << OFFSET_FOR_TIMESTAMPS)
#define PAYLOAD_DELTA_TIMESTAMPS (1 << OFFSET_FOR_TIMESTAMPS)
#define PAYLOAD_TWO_BYTE_TIME_STAMPS (2 << OFFSET_FOR_TIMESTAMPS)
#define PAYLOAD_THREE_BYTE_TIME_STAMPS (3 << OFFSET_FOR_TIMESTAMPS)
#define PAYLOAD_FOUR_BYTE_TIME_STAMPS (4 << OFFSET_FOR_TIMESTAMPS)

// payload for retina size
#define PAYLOAD_RETINA_NO_DOWN_SAMPLING_IN_PAYLOAD \
    (0 << OFFSET_FOR_RETINA_SIZE)
#define PAYLOAD_RETINA_NO_DOWN_SAMPLING (1 << OFFSET_FOR_RETINA_SIZE)
#define PAYLOAD_RETINA_64_DOWN_SAMPLING (2 << OFFSET_FOR_RETINA_SIZE)
#define PAYLOAD_RETINA_32_DOWN_SAMPLING (3 << OFFSET_FOR_RETINA_SIZE)
#define PAYLOAD_RETINA_16_DOWN_SAMPLING (4 << OFFSET_FOR_RETINA_SIZE)

// payload for master slave
#define PAYLOAD_MASTER_SLAVE_USE_INTERNAL_COUNTER 0
#define PAYLOAD_MASTER_SLAVE_SET_SLAVE 1
#define PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_NOT_STARTED 2
#define PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_ACTIVE 4

uint32_t _mode = NULL;
uint32_t _protocol_key_offset = NULL;

//! human readable definitions of each mode
typedef enum modes_e{
    RESET_TO_DEFAULT = 0,
    PUSH_BOT = 1,
    SPOMNIBOT = 2,
    BALL_BALANCER = 3,
    MY_ORO_BOTICS = 4,
    FREE = 5
} modes_e;

typedef struct multicast_packet {
    uint32_t key;
    uint32_t payload;
    uint32_t payload_flag;
}multicast_packet;

static inline void set_protocol_mode(
        uint32_t mode, uint32_t protocol_key_offset){
    _mode = mode;
    _protocol_key_offset = protocol_key_offset;

}

static inline multicast_packet get_configure_master_key_command(
        uint32_t new_key){
   return (multicast_packet){
        .key = CONFIGURE_MASTER_KEY | _protocol_key_offset,
        .payload = new_key,
        .payload_flag = WITH_PAYLOAD
   };
}

static inline multicast_packet get_set_mode_command(){
    if (_mode == PUSH_BOT){
         return (multicast_packet){
            .key = CHANGE_MODE | _protocol_key_offset,
            .payload = PAYLOAD_SET_TO_PUSH_BOT_MODE,
            .payload_flag = WITH_PAYLOAD
         };
    }else if (_mode == SPOMNIBOT){
         return (multicast_packet){
            .key = CHANGE_MODE | _protocol_key_offset,
            .payload = PAYLOAD_SET_TO_SPOMNI_BOT_MODE,
            .payload_flag = WITH_PAYLOAD
         };
    } else if (_mode == BALL_BALANCER){
         return (multicast_packet){
            .key = CHANGE_MODE | _protocol_key_offset,
            .payload = PAYLOAD_SET_TO_BALL_BALANCER_MODE,
            .payload_flag = WITH_PAYLOAD
         };
    } else if (_mode == MY_ORO_BOTICS){
         return (multicast_packet){
            .key = CHANGE_MODE | _protocol_key_offset,
            .payload = PAYLOAD_SET_TO_MY_OROBOTICS_PROJECT_MODE,
            .payload_flag = WITH_PAYLOAD
         };
    } else if (_mode == FREE){
         return (multicast_packet){
            .key = CHANGE_MODE | _protocol_key_offset,
            .payload = PAYLOAD_SET_TO_FREE_MODE,
            .payload_flag = WITH_PAYLOAD
         };
    }

    log_error("The mode given is not recognised within this protocol.");
    rt_error(RTE_API);
}

static inline multicast_packet set_retina_transmission_key(
        uint32_t new_key, uint32_t uart_id){

     return (multicast_packet){
        .key = (ACTIVE_RETINA_EVENT_STREAMING_SET_KEY |
                (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = new_key,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet disable_retina_event_streaming(uint32_t uart_id){
     return (multicast_packet){
        .key = (DISABLE_RETINA_EVENT_STREAMING |
                (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = 0,
        .payload_flag = NO_PAYLOAD
     };
}

static inline multicast_packet master_slave_use_internal_counter(
        uint32_t uart_id){
     return (multicast_packet){
        .key = (MASTER_SLAVE_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                _protocol_key_offset),
        .payload = PAYLOAD_MASTER_SLAVE_USE_INTERNAL_COUNTER,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet master_slave_set_slave(uint32_t uart_id){
     return (multicast_packet){
        .key = (MASTER_SLAVE_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                _protocol_key_offset),
        .payload = PAYLOAD_MASTER_SLAVE_SET_SLAVE,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet master_slave_set_master_clock_not_started(
        uint32_t uart_id){
     return (multicast_packet){
        .key = (MASTER_SLAVE_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                _protocol_key_offset),
        .payload = PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_NOT_STARTED,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet master_slave_set_master_clock_active(
        uint32_t uart_id){
     return (multicast_packet){
        .key = (MASTER_SLAVE_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                _protocol_key_offset),
        .payload = PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_ACTIVE,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet bias_values(
        uint32_t bias_id, uint32_t bias_value, uint32_t uart_id){
     return (multicast_packet){
        .key = (MASTER_SLAVE_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                _protocol_key_offset),
        .payload = PAYLOAD_MASTER_SLAVE_SET_MASTER_CLOCK_ACTIVE,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet reset_retina(uint32_t uart_id){
     return (multicast_packet){
        .key = (RESET_RETINA_KEY | (uart_id << OFFSET_FOR_UART_ID) |
                _protocol_key_offset),
        .payload = 0,
        .payload_flag = NO_PAYLOAD
     };
}

static inline multicast_packet turn_off_sensor_reporting(uint32_t sensor_id){
     return (multicast_packet){
        .key = SENSOR_REPORTING_OFF_KEY | _protocol_key_offset,
        .payload = (sensor_id << SENSOR_ID_OFFSET),
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet poll_sensors_once(uint32_t sensor_id){
     return (multicast_packet){
        .key = POLL_SENSORS_ONCE_KEY | _protocol_key_offset,
        .payload = (sensor_id << SENSOR_ID_OFFSET),
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet poll_individual_sensor_continuously(
        uint32_t sensor_id, uint32_t time_in_ms){
     return (multicast_packet){
        .key = POLL_SENSORS_CONTINUOUSLY_KEY | _protocol_key_offset,
        .payload = ((sensor_id << SENSOR_ID_OFFSET) |
                      (time_in_ms << OFFSET_FOR_SENSOR_TIME)),
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet generic_motor_enable_disable(
        uint32_t enable_disable, uint32_t uart_id){
     return (multicast_packet){
        .key = DISABLE_MOTOR_KEY | (uart_id << OFFSET_FOR_UART_ID) |
               _protocol_key_offset,
        .payload = enable_disable,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet generic_motor_total_period_duration(
        uint32_t time_in_ms, uint32_t uart_id){
     return (multicast_packet){
        .key = MOTOR_RUN_FOR_PERIOD_KEY | (uart_id << OFFSET_FOR_UART_ID) |
               _protocol_key_offset,
        .payload = time_in_ms,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet generic_motor0_raw_output_permanent(
        uint32_t pwm_signal, uint32_t uart_id){
     return (multicast_packet){
        .key = MOTOR_0_RAW_PERM_KEY | (uart_id << OFFSET_FOR_UART_ID) |
               _protocol_key_offset,
        .payload = pwm_signal,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet generic_motor1_raw_output_permanent(
        uint32_t pwm_signal, uint32_t uart_id){
     return (multicast_packet){
        .key = MOTOR_1_RAW_PERM_KEY | (uart_id << OFFSET_FOR_UART_ID) |
               _protocol_key_offset,
        .payload = pwm_signal,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet generic_motor0_raw_output_leak_to_0(
        uint32_t pwm_signal, uint32_t uart_id){
     return (multicast_packet){
        .key = MOTOR_0_RAW_LEAK_KEY | (uart_id << OFFSET_FOR_UART_ID) |
               _protocol_key_offset,
        .payload = pwm_signal,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet generic_motor1_raw_output_leak_to_0(
        uint32_t pwm_signal, uint32_t uart_id){
     return (multicast_packet){
        .key = MOTOR_1_RAW_LEAK_KEY | (uart_id << OFFSET_FOR_UART_ID) |
               _protocol_key_offset,
        .payload = pwm_signal,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet pwm_pin_output_timer_a_duration(
        uint32_t timer_period, uint32_t uart_id){
     return (multicast_packet){
        .key = (MOTOR_TIMER_A_TOTAL_PERIOD_KEY |
                  (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = timer_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet pwm_pin_output_timer_b_duration(
        uint32_t timer_period, uint32_t uart_id){
     return (multicast_packet){
        .key = (MOTOR_TIMER_B_TOTAL_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = timer_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet pwm_pin_output_timer_c_duration(
        uint32_t timer_period, uint32_t uart_id){
     return (multicast_packet){
        .key = (MOTOR_TIMER_C_TOTAL_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = timer_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet pwm_pin_output_timer_a_channel_0_ratio(
        uint32_t timer_period, uint32_t uart_id){
     return (multicast_packet){
        .key = (MOTOR_TIMER_A_CHANNEL_0_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = timer_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet pwm_pin_output_timer_a_channel_1_ratio(
        uint32_t timer_period, uint32_t uart_id){
     return (multicast_packet){
        .key = (MOTOR_TIMER_A_CHANNEL_1_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = timer_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet pwm_pin_output_timer_b_channel_0_ratio(
        uint32_t timer_period, uint32_t uart_id){
     return (multicast_packet){
        .key = (MOTOR_TIMER_B_CHANNEL_0_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = timer_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet pwm_pin_output_timer_b_channel_1_ratio(
        uint32_t timer_period, uint32_t uart_id){
     return (multicast_packet){
        .key = (MOTOR_TIMER_B_CHANNEL_1_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = timer_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet pwm_pin_output_timer_c_channel_0_ratio(
        uint32_t timer_period, uint32_t uart_id){
     return (multicast_packet){
        .key = (MOTOR_TIMER_C_CHANNEL_0_ACTIVE_PERIOD_KEY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = timer_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet pwm_pin_output_timer_c_channel_1_ratio(
        uint32_t timer_period, uint32_t uart_id){
     return (multicast_packet){
        .key = (MOTOR_TIMER_C_CHANNEL_1_ACTIVE_PERIOD_KEY  |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = timer_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet query_state_of_io_lines(){
     return (multicast_packet){
        .key = QUERY_STATES_LINES_KEY | _protocol_key_offset,
        .payload = 0,
        .payload_flag = NO_PAYLOAD
     };
}

static inline multicast_packet set_output_pattern_for_payload(uint32_t payload){
     return (multicast_packet){
        .key = SET_OUTPUT_PATTERN_KEY | _protocol_key_offset,
        .payload = payload,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet add_payload_logic_to_current_output(
        uint32_t payload){
     return (multicast_packet){
        .key = ADD_PAYLOAD_TO_CURRENT_OUTPUT_KEY | _protocol_key_offset,
        .payload = payload,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet remove_payload_logic_to_current_output(
        uint32_t payload){
     return (multicast_packet){
        .key = REMOVE_PAYLOAD_TO_CURRENT_OUTPUT_KEY | _protocol_key_offset,
        .payload = payload,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet set_payload_pins_to_high_impedance(
        uint32_t payload){
     return (multicast_packet){
        .key = SET_PAYLOAD_TO_HIGH_IMPEDANCE_KEY | _protocol_key_offset,
        .payload = payload,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_laser_config_total_period(
        uint32_t total_period, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
            "The mode you configured is not the push bot, and so this "
            "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_LASER_CONFIG_TOTAL_PERIOD |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = total_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_laser_config_active_time(
        uint32_t active_time, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
            "The mode you configured is not the push bot, and so this "
            "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_LASER_CONFIG_ACTIVE_TIME |
                  (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = active_time,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_laser_set_frequency(
        uint32_t frequency, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_LASER_FREQUENCY | _protocol_key_offset |
                 (uart_id << PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER)),
        .payload = frequency,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_speaker_config_total_period(
        uint32_t total_period, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_SPEAKER_CONFIG_TOTAL_PERIOD |
                (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = total_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_speaker_config_active_time(
        uint32_t active_time, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_SPEAKER_CONFIG_ACTIVE_TIME |
                (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = active_time,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_speaker_set_tone(
        uint32_t frequency, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_SPEAKER_TONE_BEEP | _protocol_key_offset |
                 (uart_id << PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER)),
        .payload = frequency,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_speaker_set_melody(
        uint32_t melody, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_SPEAKER_TONE_MELODY | _protocol_key_offset |
                 (uart_id << PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER)),
        .payload = melody,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_led_total_period(
        uint32_t total_period, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_LED_CONFIG_TOTAL_PERIOD |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = total_period,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_led_back_active_time( 
        uint32_t active_time, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_LED_BACK_CONFIG_ACTIVE_TIME |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = active_time,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_led_front_active_time( 
        uint32_t active_time, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_LED_FRONT_CONFIG_ACTIVE_TIME |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = active_time,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_led_set_frequency(
        uint32_t frequency, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_LED_FREQUENCY | _protocol_key_offset |
                 (uart_id << PUSH_BOT_UART_OFFSET_SPEAKER_LED_LASER)),
        .payload = frequency,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_motor_0_permanent( 
        state_t velocity, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_MOTOR_0_PERMANENT_VELOCITY + uart_id) |
                _protocol_key_offset,
        .payload = velocity,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_motor_1_permanent(
        uint32_t velocity, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_MOTOR_1_PERMANENT_VELOCITY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = velocity,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_motor_0_leaking_towards_zero(
        uint32_t velocity, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_MOTOR_0_LEAKY_VELOCITY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = velocity,
        .payload_flag = WITH_PAYLOAD
     };
}

static inline multicast_packet push_bot_motor_1_leaking_towards_zero(
        uint32_t velocity, uint32_t uart_id){
    if (_mode != PUSH_BOT){
        log_error(
             "The mode you configured is not the push bot, and so this "
             "message is invalid for mode %d", _mode);
    }

     return (multicast_packet){
        .key = (PUSH_BOT_MOTOR_1_LEAKY_VELOCITY |
                 (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
        .payload = velocity,
        .payload_flag = WITH_PAYLOAD
     };
}


static inline multicast_packet _key_retina(
        uint32_t retina_pixels, uint32_t time_stamps, uint32_t uart_id){
    if (retina_pixels == 128 * 128){
        // if fine, create message
         return (multicast_packet){
            .key = (ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                      (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
            .payload = (time_stamps | PAYLOAD_RETINA_NO_DOWN_SAMPLING),
            .payload_flag = WITH_PAYLOAD
         };
    }
    if (retina_pixels == 64 * 64){
         return (multicast_packet){
            .key = (ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                      (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
            .payload = (time_stamps | PAYLOAD_RETINA_64_DOWN_SAMPLING),
            .payload_flag = WITH_PAYLOAD
         };
    }
    if (retina_pixels == 32 * 32){
         return (multicast_packet){
            .key = (ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                      (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
            .payload = (time_stamps | PAYLOAD_RETINA_32_DOWN_SAMPLING),
            .payload_flag = WITH_PAYLOAD
         };
    }
    if (retina_pixels == 16 * 16){

         return (multicast_packet){
            .key = (ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                      (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
            .payload = (time_stamps | PAYLOAD_RETINA_16_DOWN_SAMPLING),
            .payload_flag = WITH_PAYLOAD
         };
    }
    else{
        log_error("The no of pixels is not supported in this protocol.");
        rt_error(RTE_API);
    }
}

static inline multicast_packet set_retina_transmission(
        bool events_in_key, uint32_t retina_pixels,
        bool payload_holds_time_stamps, uint32_t size_of_time_stamp_in_bytes,
        uint32_t uart_id){
    // if events in the key.
    if (events_in_key){
        if (!payload_holds_time_stamps){
            // not using payloads
            multicast_packet packet =
                _key_retina(retina_pixels, PAYLOAD_NO_TIMESTAMPS, uart_id);
            return packet;
        }
        else{
            // using payloads
            if (size_of_time_stamp_in_bytes == 0){
                return _key_retina(
                    retina_pixels, PAYLOAD_DELTA_TIMESTAMPS, uart_id);
            }else if(size_of_time_stamp_in_bytes == 2){
                return _key_retina(
                    retina_pixels, PAYLOAD_TWO_BYTE_TIME_STAMPS, uart_id);
            }else if(size_of_time_stamp_in_bytes == 3){
                return _key_retina(
                    retina_pixels, PAYLOAD_THREE_BYTE_TIME_STAMPS, uart_id);
            }else if(size_of_time_stamp_in_bytes == 4){
                return _key_retina(
                    retina_pixels, PAYLOAD_FOUR_BYTE_TIME_STAMPS, uart_id);
            }
        }
    }
    else{  // using payloads to hold all events

        // warn users about models
        log_warning(
            "The current SpyNNaker models do not support the reception of"
            " packets with payloads, therefore you will need to add a "
            "adaptor model between the device and spynnaker models.");

        // verify that its what the end user wants.
        if (payload_holds_time_stamps || size_of_time_stamp_in_bytes == NULL){
            log_error(
                "If you are using payloads to store events, you cannot"
                " have time stamps at all.");
            rt_error(RTE_API);
        }
        
        // if fine, create message
         return (multicast_packet){
            .key = (ACTIVE_RETINA_EVENT_STREAMING_KEYS_CONFIGURATION |
                      (uart_id << OFFSET_FOR_UART_ID) | _protocol_key_offset),
            .payload = (PAYLOAD_NO_TIMESTAMPS |
                          PAYLOAD_RETINA_NO_DOWN_SAMPLING_IN_PAYLOAD),
            .payload_flag = WITH_PAYLOAD
         };
    }
}