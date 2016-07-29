# spinn front end common imports
from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spinn_front_end_common.utility_models.reverse_ip_tag_multi_cast_source\
    import ReverseIpTagMultiCastSource

# pacman imports
from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_contiguous_range_constraint \
    import KeyAllocatorContiguousRangeContraint

# spynnaker imports
from spynnaker.pyNN.utilities import conf

# general imports
import sys


class SpikeInjector(ReverseIpTagMultiCastSource,
                    AbstractProvidesOutgoingPartitionConstraints):
    """ An Injector of Spikes for PyNN populations.  This only allows the user\
        to specify the virtual_key of the population to identify the population
    """

    model_based_max_atoms_per_core = sys.maxint

    population_parameters = {
        'machine_time_step', 'time_scale_factor', 'port', 'virtual_key',
        'database_notify_port_num', 'database_notify_host',
        'database_ack_port_num'}

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

    @staticmethod
    def recording_types(_):
        return []

    model_name = "SpikeInjector"

    def __init__(
            self, bag_of_neurons, label="SpikeSourceArray", constraints=None):

        # get database notification protocol data items.
        database_notify_port_num = bag_of_neurons[0].\
            get_population_parameter('database_notify_port_num')
        database_notify_host = bag_of_neurons[0].\
            get_population_parameter('database_notify_host')
        database_ack_port_num = bag_of_neurons[0].\
            get_population_parameter('database_ack_port_num')

        # get defaults as required.
        if database_notify_port_num is None:
            database_notify_port_num = conf.config.getint(
                "Database", "notify_port")
            for atom in bag_of_neurons:
                atom.set_population_parameter(
                    "database_notify_port_num", database_notify_port_num)

        if database_notify_host is None:
            database_notify_host = conf.config.get(
                "Database", "notify_hostname")
            for atom in bag_of_neurons:
                atom.set_population_parameter(
                    "database_notify_host", database_notify_host)

        if database_ack_port_num is None:
            database_ack_port_num = conf.config.get("Database", "listen_port")
            if database_ack_port_num == "None":
                database_ack_port_num = None
            for atom in bag_of_neurons:
                atom.set_population_parameter(
                    "database_ack_port_num", database_ack_port_num)

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

        # push to RITMCS interface
        ReverseIpTagMultiCastSource.__init__(
            self, n_keys=len(bag_of_neurons),
            machine_time_step=machine_time_step,
            timescale_factor=time_scale_factor, label=label, receive_port=port,
            virtual_key=virtual_key, constraints=constraints,
            send_buffer_notification_port=database_notify_port_num,
            send_buffer_notification_ip_address=database_notify_host,
            send_buffer_notification_ack_port=database_ack_port_num)
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

    @staticmethod
    def create_vertex(bag_of_neurons, population_parameters):
        """
        creates a SpikeInjector vertex for a bag of atoms.
        :param bag_of_neurons: the bag of atoms to put into a  vertex
        :param population_parameters: the params to push to teh vertex
        :return: a vertex
        """
        # add bag of atoms to the params
        params = dict(population_parameters)
        params['bag_of_neurons'] = bag_of_neurons

        # create and return the vertex
        vertex = SpikeInjector(**params)
        return vertex

    def get_outgoing_partition_constraints(self, partition, graph_mapper):
        """
        get any constraints for edges coming out of this vertex
        :param partition: the partition id to consider
        :param graph_mapper: the mapping between graphs.
        :return: list of constraints.
        """
        constraints = ReverseIpTagMultiCastSource\
            .get_outgoing_partition_constraints(self, partition, graph_mapper)
        constraints.append(KeyAllocatorContiguousRangeContraint())
        return constraints
