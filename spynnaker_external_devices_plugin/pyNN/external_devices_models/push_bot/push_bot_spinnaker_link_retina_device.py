# pynn imports

from pacman.executor.injection_decorator import inject, supports_injection
from spinn_front_end_common.abstract_models.impl.provides_key_to_atom_mapping_impl import \
    ProvidesKeyToAtomMappingImpl
from spynnaker.pyNN.utilities import constants
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    push_bot.push_bot_retina_device import \
    PushBotRetinaDevice


@supports_injection
class PushBotSpiNNakerLinkRetinaDevice(
        PushBotRetinaDevice, ProvidesKeyToAtomMappingImpl):

    def __init__(
            self, spinnaker_link_id, label=None,
            polarity=PushBotRetinaDevice.PushBotRetinaPolarity.Merged,
            n_neurons=
            PushBotRetinaDevice.PushBotRetinaResolution.Native128.value,
            board_address=None):

        PushBotRetinaDevice.__init__(
            self, spinnaker_link_id, label,
            polarity, n_neurons, board_address)
        ProvidesKeyToAtomMappingImpl.__init__(self)

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