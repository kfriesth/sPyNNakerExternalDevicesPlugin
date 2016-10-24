
# pynn imports
from spinn_front_end_common.abstract_models.impl.\
    provides_key_to_atom_mapping_impl import \
    ProvidesKeyToAtomMappingImpl
from spinn_front_end_common.abstract_models.impl.\
    send_me_multicast_commands_vertex import SendMeMulticastCommandsVertex
from spynnaker_external_devices_plugin.pyNN.protocols.\
    munich_io_spinnaker_link_protocol import MunichIoSpiNNakerLinkProtocol

UART_ID = 0


class PushBotLaserDevice(
        SendMeMulticastCommandsVertex, ProvidesKeyToAtomMappingImpl):

    def __init__(
            self, uart_id=0, start_active_time=0,
            start_total_period=0, start_frequency=0,
            command_sender_protocol=None):

        # munich protocol
        self._control_module_protocol = MunichIoSpiNNakerLinkProtocol(
            mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)
        if command_sender_protocol is None:
            self._protocol = self._control_module_protocol
        else:
            self._protocol = command_sender_protocol

        # protocol specific data items
        self._uart_id = uart_id
        self._start_active_time = start_active_time
        self._start_total_period = start_total_period
        self._start_frequency = start_frequency

        SendMeMulticastCommandsVertex.__init__(
            self, start_resume_commands=self._get_start_resume_commands(),
            pause_stop_commands=self._get_pause_stop_commands(),
            timed_commands=self._get_timed_commands())
        ProvidesKeyToAtomMappingImpl.__init__(self)

    def _get_start_resume_commands(self):
        commands = list()

        # add mode command if not done already
        if not self._protocol.has_set_off_configuration_command():
            commands.append(self._protocol.get_set_mode_command())

        # device specific commands
        commands.append(self._protocol.push_bot_laser_config_total_period(
            total_period=self._start_total_period, uart_id=self._uart_id,
            time=0))
        commands.append(self._protocol.push_bot_laser_config_active_time(
            active_time=self._start_active_time, uart_id=self._uart_id,
            time=0))
        commands.append(self._protocol.push_bot_laser_set_frequency(
            frequency=self._start_frequency, uart_id=self._uart_id, time=0))
        return commands

    def _get_pause_stop_commands(self):
        commands = list()
        commands.append(self._protocol.push_bot_laser_config_total_period(
            total_period=0, uart_id=self._uart_id, time=0))
        commands.append(self._protocol.push_bot_laser_config_active_time(
            active_time=0, uart_id=self._uart_id, time=0))
        commands.append(self._protocol.push_bot_laser_set_frequency(
            frequency=0, uart_id=self._uart_id, time=0))
        return commands

    @staticmethod
    def _get_timed_commands():
        return []

    @property
    def uart_id(self):
        return self._uart_id

    @property
    def protocol_instance_key(self):
        return self._control_module_protocol.instance_key

    @property
    def frequency_key(self):
        return self._control_module_protocol.push_bot_laser_set_frequency(
            0, self._uart_id).key

    @property
    def active_time_key(self):
        return self._control_module_protocol.push_bot_laser_config_active_time(
            0, self._uart_id).key

    @property
    def total_period_key(self):
        return self._control_module_protocol.\
            push_bot_laser_config_total_period(0, self._uart_id).key

    @property
    def model_name(self):
        return "push bot laser device"