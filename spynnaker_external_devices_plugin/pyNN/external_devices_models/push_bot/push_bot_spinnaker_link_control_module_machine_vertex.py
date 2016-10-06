from enum import Enum

from pacman.model.decorators.overrides import overrides
from pacman.model.graphs.machine.impl.machine_vertex import MachineVertex
from spinn_front_end_common.abstract_models.\
    abstract_binary_uses_simulation_run import \
    AbstractBinaryUsesSimulationRun
from spinn_front_end_common.abstract_models.\
    abstract_has_associated_binary import \
    AbstractHasAssociatedBinary
from spinn_front_end_common.interface.provenance.\
    provides_provenance_data_from_machine_impl import \
    ProvidesProvenanceDataFromMachineImpl
from spinn_front_end_common.interface.simulation import simulation_utilities
from spinn_front_end_common.utilities import constants
from spynnaker.pyNN.models.neuron.input_types.input_type_current import \
    InputTypeCurrent


class PushBotSpiNNakerLinkControlModuleMachineVertex(
        MachineVertex, ProvidesProvenanceDataFromMachineImpl,
        AbstractHasAssociatedBinary, AbstractBinaryUsesSimulationRun):
    """PushBotSpiNNakerLinkControlModuleMachineVertex: the machine vertex
    representation of the push bot spinnaker link control module app vertex

    """

    # Regions for populations
    # 2,3,4 are taken from POPULATION_BASED_REGIONS till hack is fixed
    DATA_REGIONS = Enum(
        value="DATA_REGIONS",
        names=[('SYSTEM_REGION', 0),
               ('COMMANDS_TO_KEYS', 1),
               ('PROVENANCE_REGION', 5)])

    N_KEYS = 17
    N_KEYS_REGION_SIZE = N_KEYS * 4
    TOTAL_REQUIRED_MALLOCS = 3

    def __init__(
            self, resources_required, constraints, label, partition_id_to_key,
            synaptic_manager, vertex_slice):

        ProvidesProvenanceDataFromMachineImpl.__init__(
            self, self.DATA_REGIONS.PROVENANCE_REGION.value,
            n_additional_data_items=0)
        MachineVertex.__init__(self, resources_required, label, constraints)
        self._partition_id_to_key = partition_id_to_key
        self._synaptic_manager = synaptic_manager
        self._vertex_slice = vertex_slice
        self._input_type = InputTypeCurrent()

    def generate_data_specification(
            self, spec, placement, machine_time_step, time_scale_factor,
            machine_graph, application_graph, routing_info, graph_mapper,):
        """

        :param spec:
        :param placement:
        :param machine_time_step:
        :param time_scale_factor:
        :return:
        """

        # reverse memory regions
        self._reserve_memory_regions(spec, placement.vertex)

        # Write system region
        spec.comment(
            "\n*** Spec for push bot spinnaker link control module ***\n\n")
        spec.switch_write_focus(
            self.DATA_REGIONS.SYSTEM_REGION.value)
        spec.write_array(simulation_utilities.get_simulation_header_array(
            self.get_binary_file_name(), machine_time_step,
            time_scale_factor))

        # write keys
        spec.switch_write_focus(region=self.DATA_REGIONS.COMMANDS_TO_KEYS.value)
        self._write_command_keys(spec)

        # allow the synaptic matrix to write its data spec-able data
        self._synaptic_manager.write_data_spec(
            spec, self, self._vertex_slice, placement.vertex, placement,
            machine_graph, application_graph, routing_info, graph_mapper,
            self._input_type, machine_time_step)

        # End-of-Spec:
        spec.end_specification()

    def _reserve_memory_regions(self, spec, vertex):
        spec.comment("\nReserving memory space for data regions:\n\n")

        # Reserve memory:
        spec.reserve_memory_region(
            region=self.DATA_REGIONS.SYSTEM_REGION.value,
            size=constants.SYSTEM_BYTES_REQUIREMENT, label='System')

        spec.reserve_memory_region(
            region=self.DATA_REGIONS.COMMANDS_TO_KEYS.value,
            size=self.N_KEYS_REGION_SIZE, label='commands')

        vertex.reserve_provenance_data_region(spec)


    def _write_command_keys(self, spec):
        """ write the command keys for each partition

        :return:
        """
        for key in self._partition_id_to_key.values():
            spec.write_value(key)

    @overrides(AbstractHasAssociatedBinary.get_binary_file_name)
    def get_binary_file_name(self):
        """ Return a string representation of the models binary

        :return:
        """
        return 'push_bot_control_module.aplx'

    @staticmethod
    def get_number_of_mallocs_used_by_dsg():
        return PushBotSpiNNakerLinkControlModuleMachineVertex.\
            TOTAL_REQUIRED_MALLOCS
