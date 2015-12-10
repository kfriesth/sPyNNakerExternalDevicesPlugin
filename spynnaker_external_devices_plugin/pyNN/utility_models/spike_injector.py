from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_edge_constraints import \
    AbstractProvidesOutgoingEdgeConstraints
from spinn_front_end_common.utility_models.reverse_ip_tag_multi_cast_source\
    import ReverseIpTagMultiCastSource

from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_contiguous_range_constraint \
    import KeyAllocatorContiguousRangeContraint


class SpikeInjector(ReverseIpTagMultiCastSource,
                    AbstractProvidesOutgoingEdgeConstraints):
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

    def get_outgoing_edge_constraints(self, partitioned_edge, graph_mapper):
        constraints = ReverseIpTagMultiCastSource\
            .get_outgoing_edge_constraints(
                self, partitioned_edge, graph_mapper)
        constraints.append(KeyAllocatorContiguousRangeContraint())
        return constraints

    @property
    def change_requires_mapping(self):
        """
        property for checking if someting has changed
        :return:
        """
        return self._change_requires_mapping

    @change_requires_mapping.setter
    def change_requires_mapping(self, new_value):
        """
        setter for the changed property
        :param new_value: the new state to change it to
        :return:
        """
        self._change_requires_mapping = new_value
