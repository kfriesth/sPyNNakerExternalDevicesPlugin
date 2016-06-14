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

        _spinnaker = get_spynnaker()

        # locate the live spike recorder
        if (port, hostname) in self._live_spike_recorders:
            live_spike_recorder = self._live_spike_recorders[(port, hostname)]
        else:
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

            live_spike_recorder = _spinnaker.create_population(
                size=1, cellclass=LiveSpikeGather, cellparams=cellparams,
                structure=None, label="LiveSpikeReceiver")
            self._live_spike_recorders[(port, hostname)] = live_spike_recorder

        self.add_edge(population_to_get_live_output_from, live_spike_recorder)

    def add_edge(self, pre_population, post_population):
        _spinnaker = get_spynnaker()
        _spinnaker.add_extra_edge(
            pre_population, post_population, PARTITION_ID)