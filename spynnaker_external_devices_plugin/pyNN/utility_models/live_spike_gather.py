# spinn front end common imports
from spinn_front_end_common.utility_models.live_packet_gather import \
    LivePacketGather

# spinnman imports
from spinnman.messages.eieio.eieio_type import EIEIOType


class LiveSpikeGather(LivePacketGather):
    """
    encapsulation class to convert from bag of atoms interface to normal
    class hierarchy format.
    """

    population_parameters = {
        'machine_time_step', 'time_scale_factor', 'ip_address',
        'port', 'database_notification_port_number', 'database_notify_host',
        'database_ack_port_number', 'board_address', 'tag', 'strip_sdp',
        'use_prefix', 'key_prefix', 'prefix_type', 'message_type',
        'right_shift', 'payload_as_time_stamps', 'use_payload_prefix',
        'payload_prefix', 'payload_right_shift',
        'number_of_packets_sent_per_time_step'}

    @staticmethod
    def default_parameters(_):
        return {}

    @staticmethod
    def fixed_parameters(_):
        return {}

    @staticmethod
    def state_variables(_):
        return list()

    @staticmethod
    def is_array_parameters(_):
        return {}

    model_name = "LiveSpikeInjector"

    def __init__(self, bag_of_neurons, label, constraints):

        # determine machine time step
        machine_time_step = \
            bag_of_neurons[0].get_population_parameter('machine_time_step')

        # determine time scale factor
        time_scale_factor = \
            bag_of_neurons[0].get_population_parameter('time_scale_factor')

        # determine ip_address
        ip_address = bag_of_neurons[0].get_population_parameter('ip_address')

        # determine port
        port = bag_of_neurons[0].get_population_parameter('port')

        # determine database_notification_port_number
        database_notification_port_number = \
            bag_of_neurons[0].get_population_parameter(
                'database_notification_port_number')

        # determine database_notify_host
        database_notify_host = \
            bag_of_neurons[0].get_population_parameter('database_notify_host')

        # determine database_ack_port_number
        database_ack_port_number = bag_of_neurons[0].get_population_parameter(
            'database_ack_port_number')

        # determine board_address
        board_address =\
            bag_of_neurons[0].get_population_parameter('board_address')

        # determine tag
        tag = bag_of_neurons[0].get_population_parameter('tag')

        # determine strip sdp
        strip_sdp = bag_of_neurons[0].get_population_parameter('strip_sdp')
        if strip_sdp is None:
            strip_sdp = True

        # determine use_prefix
        use_prefix = bag_of_neurons[0].get_population_parameter('use_prefix')
        if use_prefix is None:
            use_prefix = False

        # determine key_prefix
        key_prefix = bag_of_neurons[0].get_population_parameter('key_prefix')

        # determine prefix_type
        prefix_type = bag_of_neurons[0].get_population_parameter('prefix_type')

        # determine message_type
        message_type = \
            bag_of_neurons[0].get_population_parameter('message_type')
        if message_type is None:
            message_type = EIEIOType.KEY_32_BIT

        # determine right_shift
        right_shift = bag_of_neurons[0].get_population_parameter('right_shift')
        if right_shift is None:
            right_shift = 0

        # determine payload_as_time_stamps
        payload_as_time_stamps = \
            bag_of_neurons[0].get_population_parameter('payload_as_time_stamps')
        if payload_as_time_stamps is None:
            payload_as_time_stamps = True

        # determine use_payload_prefix
        use_payload_prefix = \
            bag_of_neurons[0].get_population_parameter('use_payload_prefix')
        if use_payload_prefix is None:
            use_payload_prefix = True

        # determine payload_prefix
        payload_prefix = \
            bag_of_neurons[0].get_population_parameter('payload_prefix')

        # determine payload_right_shift
        payload_right_shift = \
            bag_of_neurons[0].get_population_parameter('payload_right_shift')
        if payload_right_shift is None:
            payload_right_shift = 0

        # determine number_of_packets_sent_per_time_step
        number_of_packets_sent_per_time_step =\
            bag_of_neurons[0].get_population_parameter(
                'number_of_packets_sent_per_time_step')
        if number_of_packets_sent_per_time_step is None:
            number_of_packets_sent_per_time_step = 0

        # push params into the LPG class in the normal way
        LivePacketGather.__init__(
            self, machine_time_step=machine_time_step,
            timescale_factor=time_scale_factor, ip_address=ip_address,
            port=port, board_address=board_address, tag=tag,
            database_notification_port_number=
            database_notification_port_number, strip_sdp=strip_sdp,
            database_notify_host=database_notify_host,
            database_ack_port_number=database_ack_port_number,
            use_prefix=use_prefix, key_prefix=key_prefix,
            prefix_type=prefix_type, message_type=message_type,
            right_shift=right_shift,
            payload_as_time_stamps=payload_as_time_stamps,
            use_payload_prefix=use_payload_prefix,
            payload_prefix=payload_prefix,
            payload_right_shift=payload_right_shift,
            number_of_packets_sent_per_time_step=
            number_of_packets_sent_per_time_step, label=label,
            constraints=constraints)

    @staticmethod
    def create_vertex(bag_of_neurons, population_parameters):
        """
        create a vertex for this bag of atoms
        :param bag_of_neurons: the bag of atoms to put into a vertex
        :param population_parameters: the params of the vertex
        :return: the vertex which contains the bag of atoms.
        """

        # add bag of atoms to params
        params = dict(population_parameters)
        params['bag_of_neurons'] = bag_of_neurons

        # build and return vertex
        vertex = LiveSpikeGather(**params)
        return vertex




