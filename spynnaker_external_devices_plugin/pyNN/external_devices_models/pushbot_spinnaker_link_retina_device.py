# pynn imports
from enum import Enum

from pacman.executor.injection_decorator import inject, supports_injection
from pacman.model.graphs.application.impl.application_spinnaker_link_vertex \
    import ApplicationSpiNNakerLinkVertex
from spynnaker.pyNN import exceptions
from spynnaker.pyNN.models.abstract_models\
    .abstract_send_me_multicast_commands_vertex \
    import AbstractSendMeMulticastCommandsVertex
from spynnaker.pyNN.utilities import constants
from spynnaker_external_devices_plugin.pyNN.protocols.\
    munich_io_spinnaker_link_protocol import MunichIoSpiNNakerLinkProtocol

PushBotRetinaResolution = Enum(
    value="PushBotRetinaResolution",
    names=[("Native128", 128*128),
           ("Downsample64", 64*64),
           ("Downsample32", 32*32),
           ("Downsample16", 16*16)])

PushBotRetinaPolarity = Enum(
    value="PushBotRetinaPolarity",
    names=["Up", "Down", "Merged"])

UART_ID = 0

@supports_injection
class PushBotRetinaDevice(ApplicationSpiNNakerLinkVertex,
                          AbstractSendMeMulticastCommandsVertex):

    def __init__(
            self, spinnaker_link_id, label=None,
            polarity=PushBotRetinaPolarity.Merged,
            n_neurons=PushBotRetinaResolution.Native128,
            board_address=None):

        # Validate number of timestamp bytes
        if not isinstance(polarity, PushBotRetinaPolarity):
            raise exceptions.SpynnakerException(
                "Pushbot retina polarity should be one of those defined in"
                " Polarity enumeration")

        # if not using all spikes,
        if polarity == PushBotRetinaPolarity.Merged:
            n_neurons *= 2

        # munich protocol
        self._protocol = MunichIoSpiNNakerLinkProtocol(
            mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)

        # holder for commands that need mods from pacman
        self._commands_that_need_payload_updating_with_key = list()

        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=n_neurons, spinnaker_link_id=spinnaker_link_id,
            max_atoms_per_core=n_neurons, label=label,
            board_address=board_address)
        AbstractSendMeMulticastCommandsVertex.__init__(
            self, start_resume_commands=self._get_start_resume_commands(),
            pause_stop_commands=self._get_pause_stop_commands(),
            timed_commands=self._get_timed_commands())

        # stores for the injection aspects
        self._graph_mapper = None
        self._routing_infos = None

    def _get_start_resume_commands(self):
        # add to tracker for keys that need updating
        new_key_command = self._protocol.set_retina_transmission_key(
                new_key=None, uart_id=UART_ID)

        self._commands_that_need_payload_updating_with_key.append(
            new_key_command)

        commands = list()
        commands.append(self._protocol.get_set_mode_command())
        commands.append(self._protocol.disable_retina_event_streaming(
            uart_id=UART_ID))
        commands.append(new_key_command)
        commands.append(self._protocol.set_retina_transmission(
            events_in_key=True, retina_pixels=self._n_atoms/2,
            payload_holds_time_stamps=False,
            size_of_time_stamp_in_bytes=None, uart_id=UART_ID, time=0))

        return commands

    def _get_pause_stop_commands(self):
        commands = list()
        commands.append(self._protocol.disable_retina_event_streaming(
            uart_id=UART_ID))
        return commands

    @staticmethod
    def _get_timed_commands():
        return []

    @inject("MemoryGraphMapper")
    def graph_mapper(self, graph_mapper):
        self._graph_mapper = graph_mapper
        if self._routing_infos is not None:
            self.update_commands_with_payload_with_key()

    @inject("MemoryRoutingInfos")
    def routing_info(self, routing_info):
        self._routing_infos = routing_info
        if self._graph_mapper is not None:
            self.update_commands_with_payload_with_key()

    def update_commands_with_payload_with_key(self):
        for command in self._commands_that_need_payload_updating_with_key:
            vert = list(self._graph_mapper.get_machine_vertices(self))[0]
            key = self._routing_infos.get_first_key_from_pre_vertex(
                vert, constants.SPIKE_PARTITION_ID)
            command.payload = key

    @property
    def model_name(self):
        return "pushbot retina device"
