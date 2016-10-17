
# pynn imports
from pacman.model.graphs.application.impl.application_spinnaker_link_vertex \
    import ApplicationSpiNNakerLinkVertex

from spinn_front_end_common.abstract_models.impl.\
    send_me_multicast_commands_vertex import SendMeMulticastCommandsVertex

from spynnaker_external_devices_plugin.pyNN.protocols.\
    munich_io_spinnaker_link_protocol import MunichIoSpiNNakerLinkProtocol

UART_ID = 0


class PushBotSpiNNakerLinkMotorDevice(ApplicationSpiNNakerLinkVertex,
                                      SendMeMulticastCommandsVertex):

    def __init__(
            self, spinnaker_link_id, motor_id=0, uart_id=0, label=None,
            n_neurons=1, board_address=None):

        # munich protocol
        self._protocol = MunichIoSpiNNakerLinkProtocol(
            mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)

        self._motor_id = motor_id
        self._uart_id = uart_id

        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=n_neurons, spinnaker_link_id=spinnaker_link_id,
            max_atoms_per_core=n_neurons, label=label,
            board_address=board_address)
        SendMeMulticastCommandsVertex.__init__(
            self, start_resume_commands=self._get_start_resume_commands(),
            pause_stop_commands=self._get_pause_stop_commands(),
            timed_commands=self._get_timed_commands())

    def _get_start_resume_commands(self):
        commands = list()

        # add mode command if not done already
        if not self._protocol.has_set_off_configuration_command():
            commands.append(self._protocol.get_set_mode_command())

        # device specific commands
        commands.append(self._protocol.generic_motor_enable_disable(
            enable_disable=1, uart_id=self._uart_id, time=0))
        return commands

    def _get_pause_stop_commands(self):
        commands = list()
        commands.append(self._protocol.generic_motor_enable_disable(
            enable_disable=1, uart_id=self._uart_id, time=-1))
        return commands

    @staticmethod
    def _get_timed_commands():
        return []

    @property
    def uart_id(self):
        return self._uart_id

    @property
    def permanent_key(self):
        if self._motor_id == 0:
            return self._protocol.push_bot_motor_0_permanent(
                0, self._uart_id).key
        else:
            return self._protocol.push_bot_motor_1_permanent(
                0, self._uart_id).key

    @property
    def leaky_key(self):
        if self._motor_id == 0:
            return self._protocol.push_bot_motor_0_leaking_towards_zero(
                0, self._uart_id).key
        else:
            return self._protocol.push_bot_motor_1_leaking_towards_zero(
                0, self._uart_id).key

    @property
    def protocol_instance_key(self):
        return self._protocol.instance_key

    @property
    def model_name(self):
        return "push_bot_motor_device"
