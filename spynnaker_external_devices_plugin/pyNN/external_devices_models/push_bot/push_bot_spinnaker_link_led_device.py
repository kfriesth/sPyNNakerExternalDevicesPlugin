

# pynn imports
from pacman.model.graphs.application.impl.application_spinnaker_link_vertex \
    import ApplicationSpiNNakerLinkVertex
from spinn_front_end_common.abstract_models.impl.\
    send_me_multicast_commands_vertex import SendMeMulticastCommandsVertex
from spynnaker_external_devices_plugin.pyNN.protocols.\
    munich_io_spinnaker_link_protocol import MunichIoSpiNNakerLinkProtocol

UART_ID = 0


class PushBotSpiNNakerLinkLEDDevice(
        ApplicationSpiNNakerLinkVertex, SendMeMulticastCommandsVertex):

    _N_LEDS = 0

    def __init__(
            self, spinnaker_link_id, uart_id=0, start_active_time=0,
            start_total_period=0, start_frequency=0, front_led=True,
            label=None, n_neurons=1,
            board_address=None):

        # munich protocol
        self._protocol = MunichIoSpiNNakerLinkProtocol(
            mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)
        self._control_module_protocol = MunichIoSpiNNakerLinkProtocol(
            mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)

        # protocol specific data items
        self._uart_id = uart_id
        self._start_active_time = start_active_time
        self._start_total_period = start_total_period
        self._start_frequency = start_frequency
        self._is_front_led = front_led

        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=n_neurons, spinnaker_link_id=spinnaker_link_id,
            max_atoms_per_core=n_neurons, label=label,
            board_address=board_address)
        SendMeMulticastCommandsVertex.__init__(
            self, start_resume_commands=self._get_start_resume_commands(),
            pause_stop_commands=self._get_pause_stop_commands(),
            timed_commands=self._get_timed_commands())
        self._N_LEDS += 1

    def _get_start_resume_commands(self):
        commands = list()
        if self._is_front_led:
            commands.append(self._protocol.push_bot_led_front_active_time(
                active_time=self._start_active_time, uart_id=self._uart_id,
                time=0))
        else:
            commands.append(self._protocol.push_bot_led_back_active_time(
                active_time=self._start_active_time, uart_id=self._uart_id,
                time=0))
        return commands

    def _get_pause_stop_commands(self):
        commands = list()
        if self._is_front_led:
            commands.append(self._protocol.push_bot_led_front_active_time(
                active_time=0, uart_id=self._uart_id, time=0))
        else:
            commands.append(self._protocol.push_bot_led_back_active_time(
                active_time=0, uart_id=self._uart_id, time=0))
        return commands

    @staticmethod
    def _get_timed_commands():
        return []

    @property
    def uart_id(self):
        return self._uart_id

    @property
    def frequency_key(self):
        return self._control_module_protocol.push_bot_led_set_frequency(
            0, self._uart_id).key

    @property
    def active_time_key(self):
        if self._is_front_led:
            return self._control_module_protocol.\
                push_bot_led_front_active_time(0, self._uart_id).key
        else:
            return self._control_module_protocol.push_bot_led_back_active_time(
                0, self._uart_id).key

    @property
    def total_period_key(self):
        return self._control_module_protocol.push_bot_led_total_period(
            0, self._uart_id).key

    @property
    def protocol_instance_key(self):
        return self._control_module_protocol.instance_key

    @property
    def model_name(self):
        return "push bot led device"
