from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spinn_front_end_common.utility_models.reverse_ip_tag_multi_cast_source\
    import ReverseIpTagMultiCastSource

from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_contiguous_range_constraint \
    import KeyAllocatorContiguousRangeContraint

from spynnaker.pyNN.utilities.conf import config


class SpikeInjector(ReverseIpTagMultiCastSource,
                    AbstractProvidesOutgoingPartitionConstraints):
    """ An Injector of Spikes for PyNN populations.  This only allows the user\
        to specify the virtual_key of the population to identify the population
    """

    def __init__(
            self, n_neurons, machine_time_step, timescale_factor, label, port,

            virtual_key=None):

        ReverseIpTagMultiCastSource.__init__(
            self, n_keys=n_neurons, machine_time_step=machine_time_step,
            timescale_factor=timescale_factor, label=label, receive_port=port,
            virtual_key=virtual_key)

    def get_outgoing_partition_constraints(
            self, partitioned_edge, graph_mapper):
        constraints = ReverseIpTagMultiCastSource\
            .get_outgoing_edge_constraints(
                self, partitioned_edge, graph_mapper)
        constraints.append(KeyAllocatorContiguousRangeContraint())
        return constraints

    def get_number_of_mallocs_used_by_dsg(self, vertex_slice, in_edges):
        mallocs = \
            ReverseIpTagMultiCastSource.get_number_of_mallocs_used_by_dsg(
                self, vertex_slice, in_edges)
        if config.getboolean("SpecExecution", "specExecOnHost"):
            return 1
        else:
            return mallocs
