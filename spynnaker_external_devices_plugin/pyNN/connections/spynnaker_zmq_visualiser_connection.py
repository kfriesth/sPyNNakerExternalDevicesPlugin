import traceback
import zmq
import struct
import numpy

from spinn_front_end_common.utilities.database.database_connection \
    import DatabaseConnection

from spinnman.connections.connection_listener import ConnectionListener
from spinnman.connections.udp_packet_connections.udp_eieio_connection \
    import UDPEIEIOConnection


# The maximum number of 32-bit keys that will fit in a packet
_MAX_FULL_KEYS_PER_PACKET = 63

# The maximum number of 16-bit keys that will fit in a packet
_MAX_HALF_KEYS_PER_PACKET = 127


class SpynnakerZMQVisualiserConnectoin(DatabaseConnection):
    """ A connection for receiving live spikes and pushing them to a visualiser
    """

    def __init__(self, remote_zmq_address, receive_labels=None,
                 local_host=None, local_port=19999):
        """

        :param event_receiver_label: The label of the LivePacketGather\
                    vertex to which received events are being sent
        :param receive_labels: Labels of vertices from which live events\
                    will be received.
        :type receive_labels: iterable of str
        :param send_labels: Labels of vertices to which live events will be\
                    sent
        :type send_labels: iterable of str
        :param local_host: Optional specification of the local hostname or\
                    ip address of the interface to listen on
        :type local_host: str
        :param local_port: Optional specification of the local port to listen\
                    on.  Must match the port that the toolchain will send the\
                    notification on (19999 by default)
        :type local_port: int

        """

        DatabaseConnection.__init__(
            self, self._start_callback,
            local_host=local_host, local_port=local_port)

        self.add_database_callback(self._read_database_callback)

        self._live_packet_gather_label = "LiveSpikeReceiver"
        self._receive_labels = receive_labels
        self._key_to_position = dict()

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind("tcp://{}".format(remote_zmq_address))
        self._machine_timestep_ms = 0

    def _read_database_callback(self, database_reader):
        self._machine_timestep_ms = \
            database_reader.get_configuration_parameter_value(
                "machine_time_step") / 1000.0

        if self._receive_labels is not None:
            receivers = dict()
            listeners = dict()

            for receive_label in self._receive_labels:
                _, port, strip_sdp = database_reader.get_live_output_details(
                    receive_label, self._live_packet_gather_label)
                if strip_sdp:
                    if port not in receivers:
                        receiver = UDPEIEIOConnection(local_port=port)
                        listener = ConnectionListener(receiver)
                        listener.add_callback(self._receive_packet_callback)
                        listener.start()
                        receivers[port] = receiver
                        listeners[port] = listener
                else:
                    raise Exception("Currently, only ip tags which strip the"
                                    " SDP headers are supported")

                n_atoms = database_reader.get_n_atoms(receive_label)
                radius = numpy.random.uniform(0.0, 1.0, (n_atoms, 1))
                theta = numpy.random.uniform(0., 1., (n_atoms, 1)) * numpy.pi
                phi = numpy.arccos(
                    1 - 2 * numpy.random.uniform(0.0, 1., (n_atoms, 1)))
                atoms_x = radius * numpy.sin(theta) * numpy.cos(phi)
                atoms_y = radius * numpy.sin(theta) * numpy.sin(phi)
                atoms_z = radius * numpy.cos(theta)

                placements = database_reader.get_placements(receive_label)
                (x, y, p, lo_atom, _) = next(placements)

                key_to_atom_id = \
                    database_reader.get_key_to_atom_id_mapping(receive_label)
                for (key, atom_id) in key_to_atom_id.iteritems():
                    while lo_atom > atom_id:
                        (x, y, p, lo_atom, _) = next(placements)
                    self._key_to_position[key] = self._get_position(
                        x, y, p,
                        atoms_x[atom_id], atoms_y[atom_id], atoms_z[atom_id])

    def _get_position(self, x, y, p, atom_x, atom_y, atom_z):
        x_center = (x * 100) + ((p % 4) * 10)
        y_center = (y * 100) + ((p / 4) * 10)
        z_center = 0

        return (x_center + atom_x, y_center + atom_y, z_center + atom_z)

    def _receive_packet_callback(self, packet):
        try:
            header = packet.eieio_header
            if not header.is_time:
                raise Exception(
                    "Only packets with a timestamp are currently considered")

            data = b""
            while packet.is_next_element:
                element = packet.next_element
                time = (element.payload * self._machine_timestep_ms) / 1000.0
                key = element.key
                if key in self._key_to_position:
                    (x, y, z) = self._key_to_position[key]
                    data += struct.pack("<ffff", time, x, y, z)
        except:
            traceback.print_exc()
