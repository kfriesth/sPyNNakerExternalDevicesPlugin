from spinnman.messages.eieio.eieio_type import EIEIOType
from spynnaker.pyNN import get_spynnaker
from spynnaker_external_devices_plugin.pyNN.utility_models.\
    live_spike_gather import LiveSpikeGather

PARTITION_ID = "SPIKE"


class SpynnakerExternalDevicePluginManager(object):

    def __init__(self):
        self._live_spike_recorders = dict()

    def add_socket_address(self, socket_address):
        """ Add a socket address to the list to be checked by the\
            notification protocol

        :param socket_address: the socket address
        :type socket_address:
        :return:
        """
        _spinnaker = get_spynnaker()
        _spinnaker._add_socket_address(socket_address)

    def add_edge_to_recorder_vertex(
            self, population_to_get_live_output_from, port, hostname,
            database_notify_port_num, database_notify_host,
            database_ack_port_num, tag=None, board_address=None,
            strip_sdp=True, use_prefix=False, key_prefix=None,
            prefix_type=None, message_type=EIEIOType.KEY_32_BIT,
            right_shift=0, payload_as_time_stamps=True,
            use_payload_prefix=True, payload_prefix=None,
            payload_right_shift=0, number_of_packets_sent_per_time_step=0):
        """
        creates / adds a edge to a LiveSpikeInjector to provide live output
        :param population_to_get_live_output_from:
        the source pop for live output
        :param port: the port number used for live output
        :param hostname: the hostname to fire live out to
        :param database_notify_port_num: the notification port number for
        the notification protocol.
        :param database_notify_host: the hostname for the notification protocol.
        :param database_ack_port_num: the port for where the notification
        protocol will receive its read database message from
        :param tag: the tag id for this live output
        :param board_address: the board address to target
        :param strip_sdp: if the messages coming out of the machine should
        have their sdp header taken away
        :param use_prefix: If the message is going to use EIEIO prefix
        :param key_prefix: The key prefix for the EIEIO message
        :param prefix_type: The prefix type of the EIEIO message
        :param message_type: The EIEIO message type for live output
        :param right_shift: The right shift of the key for the EIEIO message
        :param payload_as_time_stamps: If the EIEIO message is using the
        payload field for timestamps.
        :param use_payload_prefix: If the EIEIO message is using a
        payload prefix
        :param payload_prefix: The payload prefix for the EIEIO message
         if required.
        :param payload_right_shift: the right shift for the payload for
        the EIEIO message
        :param number_of_packets_sent_per_time_step: the number of UDP
        packets to send per timertick (band width limiter)
        :return: None
        """

        # get global spinnaker
        _spinnaker = get_spynnaker()

        # locate the live spike recorder
        if (port, hostname) in self._live_spike_recorders:
            live_spike_recorder = self._live_spike_recorders[(port, hostname)]
        else:
            # build a live spike gatherer population and add edge

            # build cell params for the population
            cellparams = {
                'machine_time_step': _spinnaker.machine_time_step,
                'time_scale_factor': _spinnaker.timescale_factor,
                'ip_address': hostname, 'port': port,
                'database_notification_port_number': database_notify_port_num,
                'database_notify_host': database_notify_host,
                'database_ack_port_number': database_ack_port_num,
                'board_address': board_address, 'tag': tag,
                'strip_sdp': strip_sdp, 'use_prefix': use_prefix,
                'key_prefix': key_prefix, 'prefix_type': prefix_type,
                'message_type': message_type, 'right_shift': right_shift,
                'payload_as_time_stamps': payload_as_time_stamps,
                'use_payload_prefix': use_payload_prefix,
                'payload_prefix': payload_prefix,
                'payload_right_shift': payload_right_shift,
                'number_of_packets_sent_per_time_step':
                    number_of_packets_sent_per_time_step}

            # create population
            live_spike_recorder = _spinnaker.create_population(
                size=1, cellclass=LiveSpikeGather, cellparams=cellparams,
                structure=None, label="LiveSpikeReceiver")

            # record pop for later usage
            self._live_spike_recorders[(port, hostname)] = live_spike_recorder

        # add edge to list of ones to add once grouping has occurred.
        self.add_edge(population_to_get_live_output_from, live_spike_recorder)

    def add_edge(self, pre_population, post_population):
        """
        helper method for adding extra edges for the partitionable graph due to
        bag of atom approach.
        :param pre_population: the source population of the edge
        :param post_population:  the destination population of the edge
        :return: None
        """
        # get spinnaker
        _spinnaker = get_spynnaker()

        # add a extra edge to be put in after grouping
        _spinnaker.add_extra_edge(
            pre_population, post_population, PARTITION_ID)