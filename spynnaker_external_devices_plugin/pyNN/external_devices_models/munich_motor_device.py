# spynnaker imports
from spynnaker.pyNN.models.abstract_models\
    .abstract_vertex_with_dependent_vertices import \
    AbstractVertexWithEdgeToDependentVertices
from spynnaker.pyNN import exceptions

# pacman imports
from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_fixed_mask_constraint \
    import KeyAllocatorFixedMaskConstraint
from spinn_front_end_common.utilities import constants
from pacman.model.abstract_classes.abstract_virtual_vertex \
    import AbstractVirtualVertex
from pacman.model.partitionable_graph.abstract_partitionable_vertex \
    import AbstractPartitionableVertex

# front end common imports
from spinn_front_end_common.abstract_models.abstract_data_specable_vertex\
    import AbstractDataSpecableVertex
from spinn_front_end_common.abstract_models\
    .abstract_provides_outgoing_partition_constraints\
    import AbstractProvidesOutgoingPartitionConstraints

from data_specification.data_specification_generator import \
    DataSpecificationGenerator

# general imports
import logging

logger = logging.getLogger(__name__)


class _MunichMotorDevice(AbstractVirtualVertex):

    population_parameters = {'spinnaker_link'}

    model_name = "external motor device"

    @staticmethod
    def default_parameters(_):
        return {}

    @staticmethod
    def fixed_parameters(_):
        return {}

    @staticmethod
    def state_variables():
        return list()

    @staticmethod
    def is_array_parameters(_):
        return {}

    def __init__(
            self, bag_of_neurons, label="External Munich Motor",
            constraints=None):

        # assume spinnaker link is same for all atoms (as pop scoped)
        spinnaker_link_id =\
            bag_of_neurons[0].get_population_parameter('spinnaker_link_id')

        AbstractVirtualVertex.__init__(
            self, 6, spinnaker_link_id,
            "External Munich Motor", max_atoms_per_core=6)

    def is_virtual_vertex(self):
        return True


class MunichMotorDevice(AbstractDataSpecableVertex,
                        AbstractPartitionableVertex,
                        AbstractVertexWithEdgeToDependentVertices,
                        AbstractProvidesOutgoingPartitionConstraints):
    """ An Omnibot motor control device - has a real vertex and an external\
        device vertex
    """

    population_parameters = {
        'spinnaker_link', 'machine_time_step', 'timescale_factor',
        'speed', 'sample_time', 'update_time', 'delay_time', 'delta_threshold',
        'continue_if_not_different'}

    model_name = "external motor device"

    @staticmethod
    def default_parameters(_):
        return {}

    @staticmethod
    def fixed_parameters(_):
        return {}

    @staticmethod
    def state_variables():
        return list()

    @staticmethod
    def is_array_parameters(_):
        return {}

    SYSTEM_REGION = 0
    PARAMS_REGION = 1

    SYSTEM_SIZE = 4 * 4
    PARAMS_SIZE = 7 * 4

    def __init__(self, bag_of_neurons, label="SpikeSourceArray",
                 constraints=None):
        """
            self, n_neurons, machine_time_step, timescale_factor,
            spinnaker_link_id, speed=30, sample_time=4096, update_time=512,
            delay_time=5, delta_threshold=23, continue_if_not_different=True,
            label="RobotMotorControl"):
        """

        if len(bag_of_neurons) != 6:
            logger.warn("The specified number of neurons for the munich motor"
                        " device has been ignored; 6 will be used instead")

        # store neurons for future use.
        self._bag_of_neurons = bag_of_neurons

        # determine machine time step
        machine_time_step = \
            bag_of_neurons[0].get_population_parameter('machine_time_step')

        # determine time scale factor
        time_scale_factor = \
            bag_of_neurons[0].get_population_parameter('time_scale_factor')

        # assume spinnaker link is same for all atoms (as pop scoped)
        spinnaker_link_id =\
            bag_of_neurons[0].get_population_parameter('spinnaker_link_id')

        AbstractDataSpecableVertex.__init__(
            self, machine_time_step, time_scale_factor)
        AbstractPartitionableVertex.__init__(self, 6, label, 6, None)
        AbstractVertexWithEdgeToDependentVertices.__init__(
            self, [_MunichMotorDevice(spinnaker_link_id)], None)
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

    def get_outgoing_partition_constraints(self, partition, graph_mapper):

        # Any key to the device will work, as long as it doesn't set the
        # management bit.  We also need enough for the configuration bits
        # and the management bit anyway
        return list([KeyAllocatorFixedMaskConstraint(0xFFFFF800)])

    def generate_data_spec(
            self, subvertex, placement, partitioned_graph, graph,
            routing_info, hostname, graph_subgraph_mapper,
            report_folder, ip_tags, reverse_ip_tags,
            write_text_specs, application_run_time_folder):
        """
        Model-specific construction of the data blocks necessary to build a
        single external retina device.
        """
        # Create new DataSpec for this processor:
        data_writer, report_writer = \
            self.get_data_spec_file_writers(
                placement.x, placement.y, placement.p, hostname, report_folder,
                write_text_specs, application_run_time_folder)

        spec = DataSpecificationGenerator(data_writer, report_writer)

        # reserve regions
        self.reserve_memory_regions(spec)

        # Write the setup region
        spec.comment("\n*** Spec for robot motor control ***\n\n")
        self._write_basic_setup_info(spec, self.SYSTEM_REGION)

        # locate correct subedge for key
        edge_key = None
        if len(graph.outgoing_edges_from_vertex(self)) != 1:
            raise exceptions.SpynnakerException(
                "This motor should only have one outgoing edge to the robot")

        partitions = partitioned_graph.\
            outgoing_edges_partitions_from_vertex(subvertex)
        for partition in partitions.values():
            edge_keys_and_masks = \
                routing_info.get_keys_and_masks_from_partition(partition)
            edge_key = edge_keys_and_masks[0].key

        # write params to memory
        spec.switch_write_focus(region=self.PARAMS_REGION)
        spec.write_value(data=edge_key)

        # determine pop based parameters
        speed = self._bag_of_neurons[0].get_population_parameter('speed')
        sample_time = \
            self._bag_of_neurons[0].get_population_parameter('sample_time')
        update_time = \
            self._bag_of_neurons[0].get_population_parameter('update_time')
        delay_time = \
            self._bag_of_neurons[0].get_population_parameter('delay_time')
        delta_threshold = \
            self._bag_of_neurons[0].get_population_parameter('delta_threshold')
        continue_if_not_different = \
            self._bag_of_neurons[0].get_population_parameter(
                'continue_if_not_different')

        spec.write_value(data=speed)
        spec.write_value(data=sample_time)
        spec.write_value(data=update_time)
        spec.write_value(data=delay_time)
        spec.write_value(data=delta_threshold)
        if continue_if_not_different:
            spec.write_value(data=1)
        else:
            spec.write_value(data=0)

        # End-of-Spec:
        spec.end_specification()
        data_writer.close()

        return data_writer.filename

    # inherited from data specable vertex
    def get_binary_file_name(self):
        return "robot_motor_control.aplx"

    def reserve_memory_regions(self, spec):
        """
        Reserve SDRAM space for memory areas:
        1) Area for information on what data to record
        2) area for start commands
        3) area for end commands
        """
        spec.comment("\nReserving memory space for data regions:\n\n")

        # Reserve memory:
        spec.reserve_memory_region(
            region=self.SYSTEM_REGION,
            size=constants.DATA_SPECABLE_BASIC_SETUP_INFO_N_WORDS * 4,
            label='setup')

        spec.reserve_memory_region(region=self.PARAMS_REGION,
                                   size=self.PARAMS_SIZE,
                                   label='params')

    def get_sdram_usage_for_atoms(self, vertex_slice, graph):
        return self.SYSTEM_SIZE + self.PARAMS_SIZE

    def get_dtcm_usage_for_atoms(self, vertex_slice, graph):
        return 0

    def get_cpu_usage_for_atoms(self, vertex_slice, graph):
        return 0

    def has_dependent_vertices(self):
        return True

    def is_data_specable(self):
        return True

    def partition_identifier_for_dependent_edge(self, _):
        return None
