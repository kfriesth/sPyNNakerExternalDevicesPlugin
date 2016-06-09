from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spinn_front_end_common.utility_models.reverse_ip_tag_multi_cast_source\
    import ReverseIpTagMultiCastSource

from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_contiguous_range_constraint \
    import KeyAllocatorContiguousRangeContraint

import sys


class SpikeInjector(ReverseIpTagMultiCastSource,
                    AbstractProvidesOutgoingPartitionConstraints):
    """ An Injector of Spikes for PyNN populations.  This only allows the user\
        to specify the virtual_key of the population to identify the population
    """

    model_based_max_atoms_per_core = sys.maxint

    population_parameters = {'machine_time_step', 'time_scale_factor', 'port',
                             'virtual_key'}

    @staticmethod
    def default_parameters(_):
        return {}

    @staticmethod
    def fixed_parameters(_):
        return {}

    @staticmethod
    def state_variables(_):
        return list()

    @staticmethod
    def is_array_parameters(_):
        return {}

    model_name = "SpikeInjector"

    def __init__(
            self, bag_of_neurons, label="SpikeSourceArray",
            constraints=None):

        # determine machine time step
        machine_time_step = \
            bag_of_neurons[0].get_population_parameter('machine_time_step')

        # determine time scale factor
        time_scale_factor = \
            bag_of_neurons[0].get_population_parameter('time_scale_factor')

        # determine port
        port = bag_of_neurons[0].get_population_parameter('port')

        # determine virtual key
        virtual_key = bag_of_neurons[0].get_population_parameter('virtual_key')

        ReverseIpTagMultiCastSource.__init__(
            self, n_keys=len(bag_of_neurons),
            machine_time_step=machine_time_step,
            timescale_factor=time_scale_factor, label=label, receive_port=port,
            virtual_key=virtual_key, constraints=constraints)
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

    def get_outgoing_partition_constraints(
            self, partition, graph_mapper):
        constraints = ReverseIpTagMultiCastSource\
            .get_outgoing_partition_constraints(self, partition, graph_mapper)
        constraints.append(KeyAllocatorContiguousRangeContraint())
        return constraints
