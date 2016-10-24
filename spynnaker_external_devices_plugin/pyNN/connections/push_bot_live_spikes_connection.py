import logging
import numpy

from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_ethernet.push_bot_ethernet_control_module_n_model import \
    PushBotEthernetControlModuleNModel

from pacman.model.constraints.placer_constraints.\
    placer_radial_placement_from_chip_constraint import \
    PlacerRadialPlacementFromChipConstraint
from spinn_front_end_common.utilities.notification_protocol.\
    socket_address import SocketAddress
from spinn_front_end_common.utility_models.commands.\
    multi_cast_command_without_payload import \
    MultiCastCommandWithoutPayload
from spinn_front_end_common.utility_models.live_packet_gather import \
    LivePacketGather
from spinnman.connections.connection_listener import ConnectionListener
from spinnman.messages.eieio.eieio_type import EIEIOType
from spynnaker.pyNN import Population
from spynnaker_external_devices_plugin.pyNN.connections.\
    push_bot_wifi_connection import PushBotWIFIConnection
from spynnaker_external_devices_plugin.pyNN.connections\
    .spynnaker_live_spikes_connection import SpynnakerLiveSpikesConnection
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_ethernet.push_bot_retina_device import \
    PushBotRetinaDevice
from spynnaker_external_devices_plugin.pyNN.protocols.\
    munich_io_ethernet_protocol import MunichIoEthernetProtocol
from spynnaker_external_devices_plugin.pyNN.utility_models.spike_injector \
    import SpikeInjector

logger = logging.getLogger(__name__)


class PushBotLiveSpikesConnection(object):
    """ A connection for receiving and sending live spikes from and to\
        SpiNNaker and a ethernet connected push bot. This in reality supports
        the close loop functionality of a neural network running on spinnaker
        which controls and reacts to packets from a ethernet connected push bot.
    """

    def __init__(
            self, spinnaker_control_packet_port,
            spinnaker_injection_packet_port, ip_address, push_bot_ip_address,
            spynnaker_external_devices, control_n_neurons, spikes_per_second,
            ring_buffer_sigma, incoming_spike_buffer_size, control_constraints,
            tau_m, cm, v_rest, v_reset, tau_syn_E, tau_syn_I, tau_refrac,
            i_offset, v_init, board_address, uart_id, laser_start_active_time,
            laser_start_total_period, laser_start_frequency,
            front_led_start_active_time, front_led_total_period,
            front_led_start_frequency, back_led_start_active_time,
            back_led_total_period, back_led_start_frequency,
            speaker_start_active_time, speaker_start_total_period,
            speaker_start_frequency, speaker_melody_value,
            motor_0_permanent_velocity_neuron_id,
            motor_0_leaky_velocity_neuron_id,
            motor_1_permanent_velocity_neuron_id,
            motor_1_leaky_velocity_neuron_id, laser_total_period_neuron_id,
            speaker_total_period_neuron_id, leds_total_period_neuron_id,
            laser_active_time_neuron_id, speaker_active_time_neuron_id,
            front_led_active_time_neuron_id, back_led_active_time_neuron_id,
            speaker_tone_frequency_neuron_id, speaker_melody_neuron_id,
            laser_frequency_neuron_id, led_frequency_neuron_id,
            database_ack_port_num, database_notify_host,
            database_notify_port_num):
        """ constructor that builds the pops and connections and sets everything
        off for making the close loop between ethernet based push bot and
        a neural network running on spinnaker.

        :param spinnaker_control_packet_port:
        :param spinnaker_injection_packet_port:
        :param ip_address:
        :param push_bot_ip_address:
        :param spynnaker_external_devices:
        :param control_n_neurons:
        :param spikes_per_second:
        :param ring_buffer_sigma:
        :param incoming_spike_buffer_size:
        :param control_constraints:
        :param tau_m:
        :param cm:
        :param v_rest:
        :param v_reset:
        :param tau_syn_E:
        :param tau_syn_I:
        :param tau_refrac:
        :param i_offset:
        :param v_init:
        :param board_address:
        :param uart_id:
        :param laser_start_active_time:
        :param laser_start_total_period:
        :param laser_start_frequency:
        :param front_led_start_active_time:
        :param front_led_total_period:
        :param front_led_start_frequency:
        :param back_led_start_active_time:
        :param back_led_total_period:
        :param back_led_start_frequency:
        :param speaker_start_active_time:
        :param speaker_start_total_period:
        :param speaker_start_frequency:
        :param speaker_melody_value:
        :param motor_0_permanent_velocity_neuron_id:
        :param motor_0_leaky_velocity_neuron_id:
        :param motor_1_permanent_velocity_neuron_id:
        :param motor_1_leaky_velocity_neuron_id:
        :param laser_total_period_neuron_id:
        :param speaker_total_period_neuron_id:
        :param leds_total_period_neuron_id:
        :param laser_active_time_neuron_id:
        :param speaker_active_time_neuron_id:
        :param front_led_active_time_neuron_id:
        :param back_led_active_time_neuron_id:
        :param speaker_tone_frequency_neuron_id:
        :param speaker_melody_neuron_id:
        :param laser_frequency_neuron_id:
        :param led_frequency_neuron_id:
        """

        # build the protocols
        self._ethernet_protocol = MunichIoEthernetProtocol()

        self._finished_start_up = False

        # set up the database socket address so that the stuff ties into
        # the notification interface
        database_socket = SocketAddress(
            listen_port=database_ack_port_num,
            notify_host_name=database_notify_host,
            notify_port_no=database_notify_port_num)

        # update socket interface with new demands.
        spynnaker_external_devices.add_socket_address(database_socket)

        # build the two spinnaker pops
        self._retina_injector_pop, self._retina_pop = \
            self._build_retina_injector(spinnaker_injection_packet_port)

        self._control_module_pop = self._build_control_module_pop(
            control_n_neurons, spikes_per_second, ring_buffer_sigma,
            incoming_spike_buffer_size, control_constraints, tau_m,
            cm, v_rest, v_reset, tau_syn_E, tau_syn_I, tau_refrac, i_offset,
            v_init, board_address, uart_id, laser_start_active_time,
            laser_start_total_period, laser_start_frequency,
            front_led_start_active_time, front_led_total_period,
            front_led_start_frequency, back_led_start_active_time,
            back_led_total_period, back_led_start_frequency,
            speaker_start_active_time, speaker_start_total_period,
            speaker_start_frequency, speaker_melody_value,
            motor_0_permanent_velocity_neuron_id,
            motor_0_leaky_velocity_neuron_id,
            motor_1_permanent_velocity_neuron_id,
            motor_1_leaky_velocity_neuron_id, laser_total_period_neuron_id,
            speaker_total_period_neuron_id, leds_total_period_neuron_id,
            laser_active_time_neuron_id, speaker_active_time_neuron_id,
            front_led_active_time_neuron_id, back_led_active_time_neuron_id,
            speaker_tone_frequency_neuron_id, speaker_melody_neuron_id,
            laser_frequency_neuron_id, led_frequency_neuron_id)
        self._control_module_pop._vertex.add_constraint(
            PlacerRadialPlacementFromChipConstraint(0,0))

        # build the gatherer
        live_packet_gather = LivePacketGather(
            ip_address, spinnaker_control_packet_port,
            message_type=EIEIOType.KEY_PAYLOAD_32_BIT,
            payload_as_time_stamps=False, use_payload_prefix=False)
        live_packet_gather.add_constraint(
            PlacerRadialPlacementFromChipConstraint(0,0))
        spynnaker_external_devices.add_application_vertex(live_packet_gather)

        # wire the outputs from the control module to the LPG
        for partition_id in \
                self._control_module_pop._vertex.all_partition_ids():
            spynnaker_external_devices.add_edge(
                self._control_module_pop._vertex, live_packet_gather,
                partition_id)

        # build the connection that handles packets to and from spinnaker
        self._spinnaker_connection = SpynnakerLiveSpikesConnection(
            receive_labels=[self._control_module_pop.label],
            send_labels=[self._retina_injector_pop.label],
            live_packet_gather_label=live_packet_gather.label)
        self._spinnaker_connection.add_receive_callback(
            self._control_module_pop.label,
            self.receive_control_packets_from_spinnaker)
        self._spinnaker_connection.add_start_callback(
            self._control_module_pop.label, self.start_callback)
        self._spinnaker_connection.add_pause_stop_callback(
            self._control_module_pop.label, self.stop_signals)

        # handle packets coming from the push bot
        self._push_bot_connection = PushBotWIFIConnection(
            local_host=push_bot_ip_address)
        self._push_bot_connection_listener = \
            ConnectionListener(self._push_bot_connection)
        self._push_bot_connection_listener.add_callback(
            self.receive_packets_from_push_bot_retina)

        # holder for partial packets
        self._old_data = None
        self._retina_packet_size = 2
        self._buffered_ascii = ''

    def receive_control_packets_from_spinnaker(self, _, atom, payload):
        """ receives packets from the control module in spinnaker and
        converts spinnaker link packets into ethernet packets adn sends them
        to the push bot.

        :param _:  label, but we know this is the control module.
        :param atom: the atom within the control module that fired
        :param payload: the payload of the spike.
        :return: None
        """
        if self._finished_start_up:
            ethernet_message = \
                self._translate_spinnaker_link_to_ethernet_commands(
                    self._control_module_pop.
                        _vertex.get_key_from_atom_mapping(atom),
                    payload)
            if ethernet_message is not None:
                self._push_bot_connection.send(ethernet_message)
            else:
                logger.warning("The command from atom {} has no corresponding"
                               " ethernet command".format(atom))

    def receive_packets_from_push_bot_retina(self, message):
        """ receives retina packets from the push bot and converts them into
        neuron spikes within the spike injector system.

        :param message: the data packet from the push bot that contains the
        retina spikes.
        :return: None
        """
        print "retina"
        neuron_ids = self._handle_packet(message)
        for neuron_id in neuron_ids:
            self._spinnaker_connection.send_spike(
                self._retina_injector_pop.label, neuron_id)

    def start_callback(self, _, spinnaker_connection):
        """ collects the commands needed for starting the simulation and then
        does a translation between spinnaker link and ethernet commands and
        sends the ethernet ones to the push bot.

        :return:
        """
        logger.info("starting to send start / pause commands to the push bot")

        # configure the listener to start listening
        self._push_bot_connection_listener.start()

        # collect commands from the push bot components
        commands = list()
        commands.extend(self._retina_pop._start_resume_commands)
        commands.extend(
            self._control_module_pop._vertex.get_start_resume_commands)

        # send the commands to the push bot
        self._send_commands(commands)

        # flag that packets can be sent now
        self._finished_start_up = True

    def stop_signals(self, _, spinnaker_connection):
        """ sends the shut down commands to the push bot bits
        :return:
        """
        self._finished_start_up = False
        commands = list()
        commands.extend(self._retina_pop._get_pause_stop_commands())
        commands.extend(
            self._control_module_pop._vertex.get_stop_pause_commands)
        self._send_commands(commands)

    def close(self):
        """ shuts down all the connections and sends the shut down commands to
        the push bot bits.

        :return:
        """
        self.stop_signals(None, None)
        self._spinnaker_connection.close()
        self._push_bot_connection.close()
        self._push_bot_connection_listener.close()

    def _send_commands(self, commands):
        """ translates spinnaker link commands into ethernet commands and then
        sends them to the push bot.

        :param commands: the set of commands to send
        :return:
        """
        for command in commands:
            if isinstance(command, MultiCastCommandWithoutPayload):
                ethernet_message = self.\
                    _translate_spinnaker_link_no_payload_to_ethernet_commands(
                        command.key)
            else:
                ethernet_message = \
                    self._translate_spinnaker_link_to_ethernet_commands(
                        command.key, command.payload)
            # if there is a mapping between spinnaker link and ethernet command
            # send packet, otherwise give a warning
            if ethernet_message is not None:
                self._push_bot_connection.send(ethernet_message)
            else:
                logger.warn("The command {} has no mapping for the ethernet "
                            "protocol currently implemented.".format(command))

    @staticmethod
    def _build_retina_injector(spinnaker_injection_packet_port):
        """ builds the spike injector stand in for the retina, and a retina pop
        (mainly for getting start and stop commands out of)

        :param spinnaker_injection_packet_port: the port to which the
        spike injector is going to recieve packets from.
        :return: the spike injector stand in pop, and a retina pop for command
        extraction.
        """

        spike_injector_pop = Population(
            PushBotRetinaDevice.PushBotRetinaResolution.
            Native128.value, SpikeInjector,
            {'port': spinnaker_injection_packet_port},
            "The_Push_bot_Retina_spike_injector")
        real_retina_pop = PushBotRetinaDevice(
            PushBotRetinaDevice.PushBotRetinaResolution.Native128.value * 2)
        return spike_injector_pop, real_retina_pop

    @staticmethod
    def _build_control_module_pop(
            control_n_neurons, spikes_per_second, ring_buffer_sigma,
            incoming_spike_buffer_size, control_constraints, tau_m,
            cm, v_rest, v_reset, tau_syn_E, tau_syn_I, tau_refrac, i_offset,
            v_init, board_address, uart_id, laser_start_active_time,
            laser_start_total_period, laser_start_frequency,
            front_led_start_active_time, front_led_total_period,
            front_led_start_frequency, back_led_start_active_time,
            back_led_total_period, back_led_start_frequency,
            speaker_start_active_time, speaker_start_total_period,
            speaker_start_frequency, speaker_melody_value,
            motor_0_permanent_velocity_neuron_id,
            motor_0_leaky_velocity_neuron_id,
            motor_1_permanent_velocity_neuron_id,
            motor_1_leaky_velocity_neuron_id, laser_total_period_neuron_id,
            speaker_total_period_neuron_id, leds_total_period_neuron_id,
            laser_active_time_neuron_id, speaker_active_time_neuron_id,
            front_led_active_time_neuron_id, back_led_active_time_neuron_id,
            speaker_tone_frequency_neuron_id, speaker_melody_neuron_id,
            laser_frequency_neuron_id, led_frequency_neuron_id):
        """ builds the control module for the ethernet connection

        :param control_n_neurons:
        :param spikes_per_second:
        :param ring_buffer_sigma:
        :param incoming_spike_buffer_size:
        :param control_constraints:
        :param tau_m:
        :param cm:
        :param v_rest:
        :param v_reset:
        :param tau_syn_E:
        :param tau_syn_I:
        :param tau_refrac:
        :param i_offset:
        :param v_init:
        :param board_address:
        :param uart_id:
        :param laser_start_active_time:
        :param laser_start_total_period:
        :param laser_start_frequency:
        :param front_led_start_active_time:
        :param front_led_total_period:
        :param front_led_start_frequency:
        :param back_led_start_active_time:
        :param back_led_total_period:
        :param back_led_start_frequency:
        :param speaker_start_active_time:
        :param speaker_start_total_period:
        :param speaker_start_frequency:
        :param speaker_melody_value:
        :param motor_0_permanent_velocity_neuron_id:
        :param motor_0_leaky_velocity_neuron_id:
        :param motor_1_permanent_velocity_neuron_id:
        :param motor_1_leaky_velocity_neuron_id:
        :param laser_total_period_neuron_id:
        :param speaker_total_period_neuron_id:
        :param leds_total_period_neuron_id:
        :param laser_active_time_neuron_id:
        :param speaker_active_time_neuron_id:
        :param front_led_active_time_neuron_id:
        :param back_led_active_time_neuron_id:
        :param speaker_tone_frequency_neuron_id:
        :param speaker_melody_neuron_id:
        :param laser_frequency_neuron_id:
        :param led_frequency_neuron_id:
        :return:
        """
        control_pop = Population(
            control_n_neurons, PushBotEthernetControlModuleNModel,
            {
                'spikes_per_second': spikes_per_second,
                'ring_buffer_sigma': ring_buffer_sigma,
                'incoming_spike_buffer_size': incoming_spike_buffer_size,
                'constraints': control_constraints,
                'tau_m': tau_m, 'cm': cm, 'v_rest': v_rest, 'v_reset': v_reset,
                'tau_syn_E': tau_syn_E, 'tau_syn_I': tau_syn_I,
                'tau_refrac': tau_refrac, 'i_offset': i_offset,
                'v_init': v_init, 'board_address': board_address,
                'uart_id': uart_id,
                'laser_start_active_time': laser_start_active_time,
                'laser_start_total_period': laser_start_total_period,
                'laser_start_frequency': laser_start_frequency,
                'front_led_start_active_time': front_led_start_active_time,
                'front_led_total_period': front_led_total_period,
                'front_led_start_frequency': front_led_start_frequency,
                'back_led_start_active_time': back_led_start_active_time,
                'back_led_total_period': back_led_total_period,
                'back_led_start_frequency': back_led_start_frequency,
                'speaker_start_active_time': speaker_start_active_time,
                'speaker_start_total_period': speaker_start_total_period,
                'speaker_start_frequency': speaker_start_frequency,
                'speaker_melody_value': speaker_melody_value,
                'motor_0_permanent_velocity_neuron_id':
                    motor_0_permanent_velocity_neuron_id,
                'motor_0_leaky_velocity_neuron_id':
                    motor_0_leaky_velocity_neuron_id,
                'motor_1_permanent_velocity_neuron_id':
                    motor_1_permanent_velocity_neuron_id,
                'motor_1_leaky_velocity_neuron_id':
                    motor_1_leaky_velocity_neuron_id,
                'laser_total_period_neuron_id': laser_total_period_neuron_id,
                'speaker_total_period_neuron_id':
                    speaker_total_period_neuron_id,
                'leds_total_period_neuron_id': leds_total_period_neuron_id,
                'laser_active_time_neuron_id': laser_active_time_neuron_id,
                'speaker_active_time_neuron_id': speaker_active_time_neuron_id,
                'front_led_active_time_neuron_id':
                    front_led_active_time_neuron_id,
                'back_led_active_time_neuron_id':
                    back_led_active_time_neuron_id,
                'speaker_tone_frequency_neuron_id':
                    speaker_tone_frequency_neuron_id,
                'speaker_melody_neuron_id': speaker_melody_neuron_id,
                'laser_frequency_neuron_id': laser_frequency_neuron_id,
                'led_frequency_neuron_id': led_frequency_neuron_id
            }, "The_Push_bot_control_module_for_ethernet_comms")
        return control_pop

    def _translate_spinnaker_link_no_payload_to_ethernet_commands(
            self, command_key):
        return self._translate_spinnaker_link_to_ethernet_commands(
            command_key, None)

    def _translate_spinnaker_link_to_ethernet_commands(
            self, command_key, command_payload):
        """ converts between spinnaker link and ethernet packet formats

        :param command_key: the spinnaker link command key
        :param command_payload:  the spinnaker link command payload
        :return: the ethernet command (including the payload) or None
        if the command doesnt meet the requirements of the ethernet command set
        """

        # disable retina key
        if command_key == self._retina_pop.disable_retina_command_key:
            return self._ethernet_protocol.disable_retina()

        # set retina key (which doesnt do much for ethernet)
        elif command_key == self._retina_pop.set_retina_command_key:
            return self._ethernet_protocol.enable_retina()

        # motor 0 leaky command
        elif (command_key ==
                  self._control_module_pop._vertex.motor_0_leaky_command_key):
            return self._ethernet_protocol.motor_0_leaky_velocity(
                command_payload)

        # motor 0 perm command
        elif (command_key ==
                  self._control_module_pop._vertex.motor_0_perm_command_key):
            return self._ethernet_protocol.motor_0_permanent_velocity(
                command_payload)

        # motor 1 leaky command
        elif (command_key ==
                  self._control_module_pop._vertex.motor_1_leaky_command_key):
            return self._ethernet_protocol.motor_1_leaky_velocity(
                command_payload)

        # motor 1 perm command
        elif (command_key ==
                  self._control_module_pop._vertex.motor_1_perm_command_key):
            return self._ethernet_protocol.motor_1_permanent_velocity(
                command_payload)

        # laser total period command
        elif (command_key == self._control_module_pop._vertex.
                laser_config_total_period_command_key):
            return self._ethernet_protocol.laser_total_period(command_payload)

        # laser active time
        elif (command_key == self._control_module_pop._vertex.
                laser_config_active_time_command_key):
            return self._ethernet_protocol.laser_active_time(command_payload)

        # laser frequency
        elif (command_key == self._control_module_pop._vertex.
                laser_config_frequency_command_key):
            return self._ethernet_protocol.laser_frequency(command_payload)

        # led total period command
        elif (command_key == self._control_module_pop._vertex.
                led_config_total_period_command_key):
            return self._ethernet_protocol.led_total_period(command_payload)

        # led active time
        elif (command_key == self._control_module_pop._vertex.
              led_config_active_time_command_key):
            return self._ethernet_protocol.led_active_time(command_payload)

        # led frequency
        elif (command_key == self._control_module_pop._vertex.
                led_config_frequency_command_key):
            return self._ethernet_protocol.led_frequency(command_payload)

        # speaker total period
        elif (command_key == self._control_module_pop._vertex.
                speaker_config_total_period_command_key):
            return self._ethernet_protocol.speaker_total_period(command_payload)

        # speaker active time
        elif (command_key == self._control_module_pop._vertex.
                speaker_config_active_time_command_key):
            return self._ethernet_protocol.speaker_active_time(command_payload)

        # speaker frequency
        elif (command_key == self._control_module_pop._vertex.
                speaker_set_tone_command_key):
            return self._ethernet_protocol.speaker_frequency(command_payload)

        # motor enable
        elif (command_key == self._control_module_pop._vertex.
                enable_motor_key):
            return self._ethernet_protocol.enable_motor()

        # motor disable
        elif (command_key == self._control_module_pop._vertex.
                disable_motor_key):
            return self._ethernet_protocol.disable_motor()
        else:
            return None

    def _handle_packet(self, data):
        """
        some code swiped from nengo for processing the packets coming
        from the retina. Looks bloody ugly.[
        :param data:
        :return:
        """

        neuron_ids = list()

        # combine it with any leftover data from last time through the loop
        if self._old_data is not None:
            data = self._old_data + data
            self._old_data = None

        if self._retina_packet_size is None:
            # no retina events, so everything should be ascii
            self._buffered_ascii += data
        else:
            # find the ascii events
            data_all = numpy.fromstring(data, numpy.uint8)
            ascii_index = numpy.where(
                data_all[::self._retina_packet_size] < 0x80)[0]

            offset = 0
            while len(ascii_index) > 0:
                # if there's an ascii event, remove it from the data
                index = ascii_index[0] * self._retina_packet_size
                stop_index = numpy.where(data_all[index:] >= 0x80)[0]
                if len(stop_index) > 0:
                    stop_index = index + stop_index[0]
                else:
                    stop_index = len(data)

                # and add it to the buffered_ascii list
                self._buffered_ascii += \
                    data[offset + index:offset + stop_index]
                data_all = numpy.hstack(
                    (data_all[:index], data_all[stop_index:]))
                offset += stop_index - index
                ascii_index = numpy.where(
                    data_all[::self._retina_packet_size] < 0x80)[0]

            # handle any partial retina packets
            extra = len(data_all) % self._retina_packet_size
            if extra != 0:
                self._old_data = data[-extra:]
                data_all = data_all[:-extra]
            if len(data_all) > 0:
                # now process those retina events
                neuron_ids.append(self._process_retina(data_all))

        # and process the ascii events too
        while '\n' in self._buffered_ascii:
            cmd, buffered_ascii = self._buffered_ascii.split('\n', 1)
            neuron_ids.append(self._process_ascii(cmd))
        return neuron_ids

    def _process_retina(self, data_all):
        print "data from nengo retina code is {}".format(data_all)

    def _process_ascii(self, cmd):
        print "data from nengo ascii is {}".format(cmd)

    @property
    def populations(self):
        """
        returns the populations that this connection is encapsulating the
        data transfer between them and the push bot over ethernet
        :return: the spike injector which is a stand in for the retina of the
        push bot, and the control module which is a stand in for the
        motors, leds, speaker, laser etc
        """
        return self._retina_injector_pop, self._control_module_pop
