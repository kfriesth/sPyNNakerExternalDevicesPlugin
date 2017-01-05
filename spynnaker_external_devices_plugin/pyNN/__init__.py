"""
The :py:mod:`spynnaker.pynn` package contains the front end specifications
and implementation for the PyNN High-level API
(http://neuralensemble.org/trac/PyNN)
"""

import logging
import os

from spinn_front_end_common.utilities.notification_protocol.socket_address \
    import SocketAddress
from spinnman.messages.eieio.eieio_type import EIEIOType
from spynnaker.pyNN.spinnaker import executable_finder
from spynnaker.pyNN.utilities import conf
from spynnaker.pyNN.utilities import constants
from spynnaker_external_devices_plugin.pyNN import model_binaries
from spynnaker_external_devices_plugin.pyNN.connections.\
    push_bot_live_spikes_connection import \
    PushBotLiveSpikesConnection
from spynnaker_external_devices_plugin.pyNN.connections\
    .spynnaker_live_spikes_connection import SpynnakerLiveSpikesConnection
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    arbitrary_fpga_device import ArbitraryFPGADevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_spinnaker_link_cochlea_device import ExternalCochleaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_spinnaker_link_fpga_retina_device import ExternalFPGARetinaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_spinnaker_link_motor_device import MunichMotorDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_spinnaker_link_retina_device import MunichRetinaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    push_bot.push_bot_ethernet.push_bot_ethernet_control_module_n_model import \
    PushBotEthernetControlModuleNModel
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link.push_bot_spinnaker_link_control_module_n_model \
    import PushBotSpinnakerLinkControlModuleNModel
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    push_bot.push_bot_spinnaker_link.\
    push_bot_spinnaker_link_accelerometer_device import \
    PushBotSpiNNakerLinkAccelerometerDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    push_bot.push_bot_spinnaker_link.push_bot_spinnaker_link_gyro_device \
    import PushBotSpiNNakerLinkGyroDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    push_bot.push_bot_spinnaker_link.push_bot_spinnaker_link_compass_device \
    import PushBotSpiNNakerLinkCompassDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link.push_bot_spinnaker_link_retina_device \
    import PushBotSpiNNakerLinkRetinaDevice
from spynnaker_external_devices_plugin.pyNN.\
    spynnaker_external_device_plugin_manager import \
    SpynnakerExternalDevicePluginManager
from spynnaker_external_devices_plugin.pyNN.utility_models.spike_injector \
    import SpikeInjector as SpynnakerExternalDeviceSpikeInjector

logger = logging.getLogger(__name__)

executable_finder.add_path(os.path.dirname(model_binaries.__file__))
spynnaker_external_devices = SpynnakerExternalDevicePluginManager()


def activate_live_output_for(
        population, database_notify_host=None, database_notify_port_num=None,
        database_ack_port_num=None, board_address=None, port=None,
        host=None, tag=None, strip_sdp=True, use_prefix=False, key_prefix=None,
        prefix_type=None, message_type=EIEIOType.KEY_32_BIT,
        right_shift=0, payload_as_time_stamps=True,
        use_payload_prefix=True, payload_prefix=None,
        payload_right_shift=0, number_of_packets_sent_per_time_step=0):
    """ Output the spikes from a given population from SpiNNaker as they
        occur in the simulation

    :param population: The population to activate the live output for
    :type population: Population
    :param database_notify_host: the hostname for the device which is\
            listening to the database notification.
    :type database_notify_host: str
    :param database_ack_port_num: the port number to which a external device\
            will acknowledge that they have finished reading the database and\
            are ready for it to start execution
    :type database_ack_port_num: int
    :param database_notify_port_num: The port number to which a external\
            device will receive the database is ready command
    :type database_notify_port_num: int
    :param board_address: A fixed board address required for the tag, or\
            None if any address is OK
    :type board_address: str
    :param key_prefix: the prefix to be applied to the key
    :type key_prefix: int or None
    :param prefix_type: if the prefix type is 32 bit or 16 bit
    :param message_type: if the message is a eieio_command message, or\
            eieio data message with 16 bit or 32 bit keys.
    :param payload_as_time_stamps:
    :param right_shift:
    :param use_payload_prefix:
    :param payload_prefix:
    :param payload_right_shift:
    :param number_of_packets_sent_per_time_step:

    :param port: The UDP port to which the live spikes will be sent.  If not\
                specified, the port will be taken from the "live_spike_port"\
                parameter in the "Recording" section of the spynnaker cfg file.
    :type port: int
    :param host: The host name or IP address to which the live spikes will be\
                sent.  If not specified, the host will be taken from the\
                "live_spike_host" parameter in the "Recording" section of the\
                spynnaker cfg file.
    :type host: str
    :param tag: The IP tag to be used for the spikes.  If not specified, one\
                will be automatically assigned
    :type tag: int
    :param strip_sdp: Determines if the SDP headers will be stripped from the\
                transmitted packet.
    :type strip_sdp: bool
    :param use_prefix: Determines if the spike packet will contain a common\
                prefix for the spikes
    :type use_prefix: bool
    """

    # get default params if none set
    if port is None:
        port = conf.config.getint("Recording", "live_spike_port")
    if host is None:
        host = conf.config.get("Recording", "live_spike_host")
    # get default params for the database socket if required

    if database_notify_port_num is None:
        database_notify_port_num = conf.config.getint("Database",
                                                      "notify_port")
    if database_notify_host is None:
        database_notify_host = conf.config.get("Database", "notify_hostname")
    if database_ack_port_num is None:
        database_ack_port_num = conf.config.get("Database", "listen_port")
        if database_ack_port_num == "None":
            database_ack_port_num = None

    # add new edge and vertex if required to spinnaker graph
    spynnaker_external_devices.add_edge_to_recorder_vertex(
        population._vertex, port, host, tag, board_address, strip_sdp,
        use_prefix, key_prefix, prefix_type, message_type, right_shift,
        payload_as_time_stamps, use_payload_prefix, payload_prefix,
        payload_right_shift, number_of_packets_sent_per_time_step)
    # build the database socket address used by the notification interface
    database_socket = SocketAddress(
        listen_port=database_ack_port_num,
        notify_host_name=database_notify_host,
        notify_port_no=database_notify_port_num)
    # update socket interface with new demands.
    spynnaker_external_devices.add_socket_address(database_socket)


def activate_live_output_to(population, device):
    """ Activate the output of spikes from a population to an external device.\
        Note that all spikes will be sent to the device.

    :param population: The pyNN population object from which spikes will be\
                sent.
    :param device: The pyNN population external device to which the spikes\
                will be sent.
    """
    spynnaker_external_devices.add_edge(
        population._get_vertex, device._get_vertex,
        constants.SPIKE_PARTITION_ID)


def SpikeInjector(
        n_neurons, label, port=None,
        virtual_key=None, database_notify_host=None,
        database_notify_port_num=None, database_ack_port_num=None):
    """ Supports adding a spike injector to the application graph.

    :param n_neurons: the number of neurons the spike injector will emulate
    :type n_neurons: int
    :param label: the label given to the population
    :type label: str
    :param port: the port number used to listen for injections of spikes
    :type port: int
    :param virtual_key: the virtual key used in the routing system
    :type virtual_key: int
    :param database_notify_host: the hostname for the device which is\
            listening to the database notification.
    :type database_notify_host: str
    :param database_ack_port_num: the port number to which a external device\
            will acknowledge that they have finished reading the database and\
            are ready for it to start execution
    :type database_ack_port_num: int
    :param database_notify_port_num: The port number to which a external\
            device will receive the database is ready command
    :type database_notify_port_num: int

    :return:
    """
    if database_notify_port_num is None:
        database_notify_port_num = conf.config.getint("Database",
                                                      "notify_port")
    if database_notify_host is None:
        database_notify_host = conf.config.get("Database", "notify_hostname")
    if database_ack_port_num is None:
        database_ack_port_num = conf.config.get("Database", "listen_port")
        if database_ack_port_num == "None":
            database_ack_port_num = None

    # build the database socket address used by the notification interface
    database_socket = SocketAddress(
        listen_port=database_ack_port_num,
        notify_host_name=database_notify_host,
        notify_port_no=database_notify_port_num)

    # update socket interface with new demands.
    spynnaker_external_devices.add_socket_address(database_socket)
    return SpynnakerExternalDeviceSpikeInjector(
        n_neurons=n_neurons, label=label, port=port, virtual_key=virtual_key)


def push_bot_ethernet_connection(
        spinnaker_control_packet_port, spinnaker_injection_packet_port,
        push_bot_ip_address, control_n_neurons, ip_address=None,
        spikes_per_second=None, ring_buffer_sigma=None,
        incoming_spike_buffer_size=None,
        # default params for the neuron model type
        tau_m=PushBotEthernetControlModuleNModel.default_parameters['tau_m'],
        cm=PushBotEthernetControlModuleNModel.default_parameters['cm'],
        v_rest=PushBotEthernetControlModuleNModel.default_parameters['v_rest'],
        v_reset=
        PushBotEthernetControlModuleNModel.default_parameters['v_reset'],
        tau_syn_E=
        PushBotEthernetControlModuleNModel.default_parameters['tau_syn_E'],
        tau_syn_I=
        PushBotEthernetControlModuleNModel.default_parameters['tau_syn_I'],
        tau_refrac=
        PushBotEthernetControlModuleNModel.default_parameters['tau_refrac'],
        i_offset=
        PushBotEthernetControlModuleNModel.default_parameters['i_offset'],
        v_init=None,
        # global for all devices that this control module works with
        board_address=None, uart_id=0, control_constraints=None,
        # the laser bespoke setup params
        laser_start_active_time=0, laser_start_total_period=0,
        laser_start_frequency=0,
        # the front led bespoke setup params
        front_led_start_active_time=0,
        front_led_total_period=0, front_led_start_frequency=0,
        # the back led bespoke setup params
        back_led_start_active_time=0,
        back_led_total_period=0, back_led_start_frequency=0,
        # the speaker bespoke setup params
        speaker_start_active_time=0, speaker_start_total_period=0,
        speaker_start_frequency=None, speaker_melody_value=None,
        # neuron_ids for devices
        motor_0_permanent_velocity_neuron_id=None,
        motor_0_leaky_velocity_neuron_id=None,
        motor_1_permanent_velocity_neuron_id=None,
        motor_1_leaky_velocity_neuron_id=None,
        laser_total_period_neuron_id=None,
        speaker_total_period_neuron_id=None,
        leds_total_period_neuron_id=None,
        laser_active_time_neuron_id=None,
        speaker_active_time_neuron_id=None,
        front_led_active_time_neuron_id=None,
        back_led_active_time_neuron_id=None,
        speaker_tone_frequency_neuron_id=None,
        speaker_melody_neuron_id=None,
        laser_frequency_neuron_id=None,
        led_frequency_neuron_id=None,
        database_notify_port_num=None, database_notify_host=None,
        database_ack_port_num=None):
    """ helper method that builds the bridge between the push bot communicating
    via wifi and the spinnaker machine its going to feed data into and receive
    data from

    :param spinnaker_control_packet_port:
    :param spinnaker_injection_packet_port:
    :param push_bot_ip_address:
    :param control_n_neurons:
    :param ip_address:
    :param spikes_per_second:
    :param ring_buffer_sigma:
    :param incoming_spike_buffer_size:
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
    :param control_constraints:
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
    :param database_notify_port_num:
    :param database_notify_host:
    :param database_ack_port_num:
    :return:
    """
    if ip_address is None:
        ip_address = conf.config.get("Recording", "live_spike_host")

    if database_notify_port_num is None:
        database_notify_port_num = conf.config.getint("Database",
                                                      "notify_port")
    if database_notify_host is None:
        database_notify_host = conf.config.get("Database", "notify_hostname")
    if database_ack_port_num is None:
        database_ack_port_num = conf.config.get("Database", "listen_port")
        if database_ack_port_num == "None":
            database_ack_port_num = None

    connection = PushBotLiveSpikesConnection(
        spinnaker_control_packet_port=spinnaker_control_packet_port,
        spinnaker_injection_packet_port=spinnaker_injection_packet_port,
        ip_address=ip_address,
        spynnaker_external_devices=spynnaker_external_devices,
        push_bot_ip_address=push_bot_ip_address,
        control_n_neurons=control_n_neurons,
        spikes_per_second=spikes_per_second,
        ring_buffer_sigma=ring_buffer_sigma,
        incoming_spike_buffer_size=incoming_spike_buffer_size,
        control_constraints=control_constraints, tau_m=tau_m, cm=cm,
        v_rest=v_rest, v_reset=v_reset, tau_syn_E=tau_syn_E,
        tau_syn_I=tau_syn_I, tau_refrac=tau_refrac, i_offset=i_offset,
        v_init=v_init, board_address=board_address, uart_id=uart_id,
        laser_start_active_time=laser_start_active_time,
        laser_start_total_period=laser_start_total_period,
        laser_start_frequency=laser_start_frequency,
        front_led_start_active_time=front_led_start_active_time,
        front_led_total_period=front_led_total_period,
        front_led_start_frequency=front_led_start_frequency,
        back_led_start_active_time=back_led_start_active_time,
        back_led_total_period=back_led_total_period,
        back_led_start_frequency=back_led_start_frequency,
        speaker_start_active_time=speaker_start_active_time,
        speaker_start_total_period=speaker_start_total_period,
        speaker_start_frequency=speaker_start_frequency,
        speaker_melody_value=speaker_melody_value,
        motor_0_permanent_velocity_neuron_id=
            motor_0_permanent_velocity_neuron_id,
        motor_0_leaky_velocity_neuron_id=motor_0_leaky_velocity_neuron_id,
        motor_1_permanent_velocity_neuron_id=
        motor_1_permanent_velocity_neuron_id,
        motor_1_leaky_velocity_neuron_id=motor_1_leaky_velocity_neuron_id,
        laser_total_period_neuron_id=laser_total_period_neuron_id,
        speaker_total_period_neuron_id=speaker_total_period_neuron_id,
        leds_total_period_neuron_id=leds_total_period_neuron_id,
        laser_active_time_neuron_id=laser_active_time_neuron_id,
        speaker_active_time_neuron_id=speaker_active_time_neuron_id,
        front_led_active_time_neuron_id=front_led_active_time_neuron_id,
        back_led_active_time_neuron_id=back_led_active_time_neuron_id,
        speaker_tone_frequency_neuron_id=speaker_tone_frequency_neuron_id,
        speaker_melody_neuron_id=speaker_melody_neuron_id,
        laser_frequency_neuron_id=laser_frequency_neuron_id,
        led_frequency_neuron_id=led_frequency_neuron_id,
        database_ack_port_num=database_ack_port_num,
        database_notify_host=database_notify_host,
        database_notify_port_num=database_notify_port_num)

    logger.warn("Due to using the Ethernet to stream the push bot data. We"
                "recommend you use the SpiNNaker link interface instead.")

    pops = connection.populations
    return pops[0], pops[1], connection


