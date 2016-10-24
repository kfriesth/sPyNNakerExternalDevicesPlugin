# pynn imports
from enum import Enum

from spinn_front_end_common.abstract_models.impl.\
    provides_key_to_atom_mapping_impl \
    import ProvidesKeyToAtomMappingImpl
from spinn_front_end_common.abstract_models.impl.\
    send_me_multicast_commands_vertex import SendMeMulticastCommandsVertex
from spynnaker_external_devices_plugin.pyNN.protocols.\
    munich_io_spinnaker_link_protocol import MunichIoSpiNNakerLinkProtocol


class PushBotRetinaDevice(
        SendMeMulticastCommandsVertex, ProvidesKeyToAtomMappingImpl):
    PushBotRetinaResolution = Enum(
        value="PushBotRetinaResolution",
        names=[("Native128", 128 * 128),
               ("Downsample64", 64 * 64),
               ("Downsample32", 32 * 32),
               ("Downsample16", 16 * 16)])

    PushBotRetinaPolarity = Enum(
        value="PushBotRetinaPolarity",
        names=["Up", "Down", "Merged"])

    UART_ID = 0

    def __init__(self, n_atoms):

        # munich protocol
        self._protocol = MunichIoSpiNNakerLinkProtocol(
            mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)

        # holder for commands that need mods from pacman
        self._commands_that_need_payload_updating_with_key = list()

        self._n_atoms=n_atoms

        SendMeMulticastCommandsVertex.__init__(
            self, start_resume_commands=self._get_start_resume_commands(),
            pause_stop_commands=self._get_pause_stop_commands(),
            timed_commands=self._get_timed_commands())
        ProvidesKeyToAtomMappingImpl.__init__(self)

    def _get_start_resume_commands(self):
        # add to tracker for keys that need updating
        new_key_command = self._protocol.set_retina_transmission_key(
                new_key=None, uart_id=self.UART_ID)

        self._commands_that_need_payload_updating_with_key.append(
            new_key_command)

        commands = list()

        # add mode command if not done already
        if not self._protocol.has_set_off_configuration_command():
            commands.append(self._protocol.get_set_mode_command())

        # device specific commands
        commands.append(self._protocol.disable_retina_event_streaming(
            uart_id=self.UART_ID))
        commands.append(new_key_command)
        commands.append(self._protocol.set_retina_transmission(
            events_in_key=True, retina_pixels=self._n_atoms/2,
            payload_holds_time_stamps=False,
            size_of_time_stamp_in_bytes=None, uart_id=self.UART_ID, time=0))

        return commands

    def _get_pause_stop_commands(self):
        commands = list()
        commands.append(self._protocol.disable_retina_event_streaming(
            uart_id=self.UART_ID))
        return commands

    @property
    def disable_retina_command_key(self):
        return self._protocol.disable_retina_event_streaming(
            uart_id=self.UART_ID).key

    @property
    def set_retina_command_key(self):
        return self._protocol.set_retina_transmission(
            events_in_key=True, retina_pixels=self._n_atoms/2,
            payload_holds_time_stamps=False,
            size_of_time_stamp_in_bytes=None, uart_id=self.UART_ID, time=0).key

    @staticmethod
    def _get_timed_commands():
        return []

    @property
    def model_name(self):
        return "push_bot_retina_device"
