# pynn imports

from pacman.executor.injection_decorator import inject, supports_injection
from pacman.model.graphs.application.impl.\
    application_spinnaker_link_vertex import \
    ApplicationSpiNNakerLinkVertex
from spynnaker.pyNN import exceptions
from spynnaker.pyNN.utilities import constants
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_ethernet.push_bot_retina_device import \
    PushBotRetinaDevice


@supports_injection
class PushBotSpiNNakerLinkRetinaDevice(
        PushBotRetinaDevice, ApplicationSpiNNakerLinkVertex):

    def __init__(
            self, spinnaker_link_id, label=None,
            polarity=PushBotRetinaDevice.PushBotRetinaPolarity.Merged,
            n_neurons=
            PushBotRetinaDevice.PushBotRetinaResolution.Native128.value,
            board_address=None):

        # Validate number of timestamp bytes
        if not isinstance(polarity, self.PushBotRetinaPolarity):
            raise exceptions.SpynnakerException(
                "Pushbot retina polarity should be one of those defined in"
                " Polarity enumeration")

        # if not using all spikes,
        if polarity == self.PushBotRetinaPolarity.Merged:
            n_neurons *= 2

        PushBotRetinaDevice.__init__(self, n_neurons)
        ApplicationSpiNNakerLinkVertex.__init__(
            self, spinnaker_link_id=spinnaker_link_id, n_atoms=n_neurons,
            board_address=board_address, label=label)

        # stores for the injection aspects
        self._graph_mapper = None
        self._routing_infos = None

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