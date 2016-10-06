
# pynn imports
from pacman.model.graphs.application.impl.application_spinnaker_link_vertex \
    import ApplicationSpiNNakerLinkVertex
from spinn_front_end_common.abstract_models.impl.\
    send_me_multicast_commands_vertex import SendMeMulticastCommandsVertex
from spynnaker_external_devices_plugin.pyNN.protocols.\
    munich_io_spinnaker_link_protocol import MunichIoSpiNNakerLinkProtocol
from spinn_front_end_common.utilities import exceptions

UART_ID = 0


class PushBotSpiNNakerLinkSpeakerDevice(
        ApplicationSpiNNakerLinkVertex, SendMeMulticastCommandsVertex):

    def __init__(
            self, spinnaker_link_id, uart_id=0, start_active_time=0,
            start_total_period=0, start_frequency=None, melody_value=None,
            label=None, n_neurons=1, board_address=None):

        # munich protocol
        self._protocol = MunichIoSpiNNakerLinkProtocol(
            mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)

        # protocol specific data items
        self._uart_id = uart_id
        self._start_active_time = start_active_time
        self._start_total_period = start_total_period
        self._start_frequency = start_frequency
        self._melody_value = melody_value

        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=n_neurons, spinnaker_link_id=spinnaker_link_id,
            max_atoms_per_core=n_neurons, label=label,
            board_address=board_address)
        SendMeMulticastCommandsVertex.__init__(
            self, start_resume_commands=self._get_start_resume_commands(),
            pause_stop_commands=self._get_pause_stop_commands(),
            timed_commands=self._get_timed_commands())

        if self._start_frequency is None and self._melody_value is None:
            raise exceptions.ConfigurationException(
                "you must set a frequency or a melody value as start up "
                "state.")
        if (self._start_frequency is not None and
                self._melody_value is not None):
            raise exceptions.ConfigurationException(
                "you must select a frequency or a melody value as start up "
                "state. Not both")

    def _get_start_resume_commands(self):
        commands = list()
        commands.append(self._protocol.push_bot_speaker_config_total_period(
            total_period=self._start_total_period, uart_id=self._uart_id,
            time=0))
        commands.append(self._protocol.push_bot_speaker_config_active_time(
            active_time=self._start_active_time, uart_id=self._uart_id,
            time=0))
        if self._start_frequency is not None:
            commands.append(self._protocol.push_bot_speaker_set_tone(
                frequency=self._start_frequency, uart_id=self._uart_id,
                time=0))
        if self._melody_value is not None:
            commands.append(self._protocol.push_bot_speaker_set_melody(
                melody=self._melody_value, uart_id=self._uart_id,
                time=0))
        return commands

    def _get_pause_stop_commands(self):
        commands = list()
        commands.append(self._protocol.push_bot_speaker_config_total_period(
            total_period=0, uart_id=self._uart_id, time=0))
        commands.append(self._protocol.push_bot_speaker_config_active_time(
            active_time=0, uart_id=self._uart_id, time=0))
        if self._start_frequency is not None:
            commands.append(self._protocol.push_bot_speaker_set_tone(
                frequency=0, uart_id=self._uart_id, time=0))
        return commands

    @staticmethod
    def _get_timed_commands():
        return []

    @property
    def melody_key(self):
        return self._protocol.push_bot_speaker_set_melody(
            melody=0, uart_id=self._uart_id, time=0).key

    @property
    def frequency_key(self):
        return self._protocol.push_bot_speaker_set_tone(
             frequency=0, uart_id=self._uart_id, time=0).key

    @property
    def active_time_key(self):
        return self._protocol.push_bot_speaker_config_active_time(
            active_time=0, uart_id=self._uart_id, time=0).key

    @property
    def total_period_key(self):
        return self._protocol.push_bot_speaker_config_total_period(
            total_period=0, uart_id=self._uart_id, time=0).key

    @property
    def uart_id(self):
        return self._uart_id

    @property
    def model_name(self):
        return "push bot speaker device"
