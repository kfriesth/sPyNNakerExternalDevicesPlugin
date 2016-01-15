from spinnman.connections.udp_packet_connections.udp_connection \
    import UDPConnection
from spinn_front_end_common.utilities.connections.live_event_connection \
    import LiveEventConnection

import struct
import time


# The maximum number of 32-bit keys that will fit in a packet
_MAX_FULL_KEYS_PER_PACKET = 63

# The maximum number of 16-bit keys that will fit in a packet
_MAX_HALF_KEYS_PER_PACKET = 127


class SpynnakerLiveSpikesConnection(LiveEventConnection):
    """ A connection for receiving and sending live spikes from and to\
        SpiNNaker and for updating Poisson rates
    """

    def __init__(
            self, receive_labels=None, send_labels=None, poisson_labels=None,
            local_host=None, local_port=19999):
        """

        :param receive_labels: Labels of population from which live spikes\
                    will be received.
        :type receive_labels: iterable of str
        :param send_labels: Labels of population to which live spikes will be\
                    sent
        :type send_labels: iterable of str
        :param poisson_labels: Labels of poisson sources to which live rate\
                    updates will be sent
        :type poisson_labels: iterable of str
        :param local_host: Optional specification of the local hostname or\
                    ip address of the interface to listen on
        :type local_host: str
        :param local_port: Optional specification of the local port to listen\
                    on.  Must match the port that the toolchain will send the\
                    notification on (19999 by default)
        :type local_port: int

        """

        LiveEventConnection.__init__(
            self, "LiveSpikeReceiver", receive_labels, send_labels,
            local_host, local_port)
        self._poisson_labels = poisson_labels
        self._poisson_sender = None
        self._poisson_address_details = dict()
        self._machine_time_step = None

        if self._poisson_labels is not None:
            for poisson_label in self._poisson_labels:
                self._init_callbacks[poisson_label] = list()
                self._start_callbacks[poisson_label] = list()

    def _read_database_callback(self, database_reader):
        LiveEventConnection._read_database_callback(self, database_reader)
        if self._poisson_labels is not None:
            if self._poisson_sender is None:
                self._poisson_sender = UDPConnection()
            for poisson_label in self._poisson_labels:
                ip_address, port = database_reader.get_live_input_details(
                    poisson_label)
                self._poisson_address_details[poisson_label] = (
                    ip_address, port)
        self._machine_time_step = \
            database_reader.get_configuration_parameter_value(
                "machine_time_step")

    def set_poisson_rate(self, label, neuron_id, rate):
        self.set_poisson_rates(label, {neuron_id: rate})

    def _send_poisson_rate_data(self, label, n_items, rate_data):
        (ip_address, port) = self._poisson_address_details[label]
        rate_data = struct.pack("<I", n_items) + rate_data
        self._poisson_sender.send_to(rate_data, (ip_address, port))
        time.sleep(0.1)

    def set_poisson_rates(self, label, rates_for_ids):
        data_size = 0
        n_items = 0
        rate_data = b""
        for (neuron_id, rate) in rates_for_ids.iteritems():
            if data_size >= 256:
                self._send_poisson_rate_data(label, n_items, rate_data)
                data_size = 0
                rate_data = b""
                n_items = 0

            # Get the data and add it to the packet
            rate_val = int(round(float(rate) * 32768.0))
            rate_data += struct.pack("<Ii", neuron_id, rate_val)
            data_size += 8
            n_items += 1

        if data_size > 0:
            self._send_poisson_rate_data(label, n_items, rate_data)

    def send_spike(self, label, neuron_id, send_full_keys=False):
        """ Send a spike from a single neuron

        :param label: The label of the population from which the spike will\
                    originate
        :type label: str
        :param neuron_id: The id of the neuron sending a spike
        :type neuron_id: int
        :param send_full_keys: Determines whether to send full 32-bit keys,\
                    getting the key for each neuron from the database, or\
                    whether to send 16-bit neuron ids directly
        :type send_full_keys: bool
        """
        self.send_spikes(label, [neuron_id], send_full_keys)

    def send_spikes(self, label, neuron_ids, send_full_keys=False):
        """ Send a number of spikes

        :param label: The label of the population from which the spikes will\
                    originate
        :type label: str
        :param neuron_ids: array-like of neuron ids sending spikes
        :type: [int]
        :param send_full_keys: Determines whether to send full 32-bit keys,\
                    getting the key for each neuron from the database, or\
                    whether to send 16-bit neuron ids directly
        :type send_full_keys: bool
        """
        self.send_events(label, neuron_ids, send_full_keys)
