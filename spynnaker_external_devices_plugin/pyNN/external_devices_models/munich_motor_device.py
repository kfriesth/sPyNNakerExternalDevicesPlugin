# spynnaker imports
from pacman.model.constraints.partitioner_constraints.\
    partitioner_maximum_size_constraint import \
    PartitionerMaximumSizeConstraint
from pacman.model.decorators.overrides import overrides
from pacman.model.graphs.machine.impl.machine_vertex import MachineVertex
from pacman.model.resources.cpu_cycles_per_tick_resource import \
    CPUCyclesPerTickResource
from pacman.model.resources.dtcm_resource import DTCMResource
from pacman.model.resources.resource_container import ResourceContainer
from pacman.model.resources.sdram_resource import SDRAMResource
from spynnaker.pyNN.models.abstract_models\
    .abstract_vertex_with_dependent_vertices import \
    AbstractVertexWithEdgeToDependentVertices
from spynnaker.pyNN import exceptions

# pacman imports
from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_fixed_mask_constraint \
    import KeyAllocatorFixedMaskConstraint
from spinn_front_end_common.utilities import constants
from pacman.model.graphs.application.impl.application_virtual_vertex \
    import ApplicationVirtualVertex
from pacman.model.graphs.application.impl.application_vertex import \
    ApplicationVertex

# front end common imports
from spinn_front_end_common.abstract_models.impl.\
    application_uses_simulation_data_specable_vertex \
    import ApplicationUsesSimulationDataSpecableVertex
from spinn_front_end_common.abstract_models\
    .abstract_provides_outgoing_partition_constraints\
    import AbstractProvidesOutgoingPartitionConstraints

# general imports
import logging

logger = logging.getLogger(__name__)

MOTOR_PARTITION_ID = "MOTOR"


class _MunichMotorDevice(ApplicationVirtualVertex):

    def __init__(self, spinnaker_link_id):

        ApplicationVirtualVertex.__init__(
            self, 6, spinnaker_link_id,
            "External Munich Motor",
            constraints=[PartitionerMaximumSizeConstraint(6)])

    @property
    @overrides(ApplicationVirtualVertex.model_name)
    def model_name(self):
        return "external motor device"


class MunichMotorDevice(ApplicationUsesSimulationDataSpecableVertex,
                        ApplicationVertex,
                        AbstractVertexWithEdgeToDependentVertices,
                        AbstractProvidesOutgoingPartitionConstraints):
    """ An Omnibot motor control device - has a real vertex and an external\
        device vertex
    """

    SYSTEM_REGION = 0
    PARAMS_REGION = 1

    PARAMS_SIZE = 7 * 4

    def __init__(
            self, n_neurons, machine_time_step, timescale_factor,
            spinnaker_link_id, speed=30, sample_time=4096, update_time=512,
            delay_time=5, delta_threshold=23, continue_if_not_different=True,
            label="RobotMotorControl"):
        """
        """

        if n_neurons != 6:
            logger.warn("The specified number of neurons for the munich motor"
                        " device has been ignored; 6 will be used instead")

        ApplicationUsesSimulationDataSpecableVertex.__init__(
            self, machine_time_step, timescale_factor)
        ApplicationVertex.__init__(self, label)
        AbstractVertexWithEdgeToDependentVertices.__init__(
            self, [_MunichMotorDevice(spinnaker_link_id)], MOTOR_PARTITION_ID)
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

        self._speed = speed
        self._sample_time = sample_time
        self._update_time = update_time
        self._delay_time = delay_time
        self._delta_threshold = delta_threshold
        self._continue_if_not_different = continue_if_not_different

    @property
    @overrides(ApplicationVertex.n_atoms)
    def n_atoms(self):
        return 6

    @overrides(ApplicationVertex.create_machine_vertex)
    def create_machine_vertex(self, vertex_slice, resources_required,
                              label=None, constraints=None):
        return MachineVertex(resources_required, label, constraints)

    @overrides(ApplicationVertex.get_resources_used_by_atoms)
    def get_resources_used_by_atoms(self, vertex_slice):
        return ResourceContainer(
            sdram=SDRAMResource(self.get_sdram_usage_for_atoms()),
            dtcm=DTCMResource(self.get_dtcm_usage_for_atoms()),
            cpu_cycles=CPUCyclesPerTickResource(
                self.get_cpu_usage_for_atoms()))

    @overrides(AbstractProvidesOutgoingPartitionConstraints.
               get_outgoing_partition_constraints)
    def get_outgoing_partition_constraints(self, partition):

        # Any key to the device will work, as long as it doesn't set the
        # management bit.  We also need enough for the configuration bits
        # and the management bit anyway
        return list([KeyAllocatorFixedMaskConstraint(0xFFFFF800)])

    @overrides(ApplicationUsesSimulationDataSpecableVertex.
               generate_application_data_specification)
    def generate_application_data_specification(
            self, spec, placement, graph_mapper, application_graph,
            machine_graph, routing_info, iptags, reverse_iptags):

        # reserve regions
        self.reserve_memory_regions(spec)

        # Write the setup region
        spec.comment("\n*** Spec for robot motor control ***\n\n")

        # handle simulation data
        spec.switch_write_focus(self.SYSTEM_REGION)
        spec.write_array(self.data_for_simulation_data())

        # Get the key
        edge_key = routing_info.get_first_key_from_pre_vertex(
            placement.vertex, MOTOR_PARTITION_ID)
        if edge_key is None:
            raise exceptions.SpynnakerException(
                "This motor should have one outgoing edge to the robot")

        # write params to memory
        spec.switch_write_focus(region=self.PARAMS_REGION)
        spec.write_value(data=edge_key)
        spec.write_value(data=self._speed)
        spec.write_value(data=self._sample_time)
        spec.write_value(data=self._update_time)
        spec.write_value(data=self._delay_time)
        spec.write_value(data=self._delta_threshold)
        if self._continue_if_not_different:
            spec.write_value(data=1)
        else:
            spec.write_value(data=0)

        # End-of-Spec:
        spec.end_specification()

    @overrides(ApplicationUsesSimulationDataSpecableVertex.get_binary_file_name)
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
            size=constants.SYSTEM_BYTES_REQUIREMENT,
            label='setup')

        spec.reserve_memory_region(region=self.PARAMS_REGION,
                                   size=self.PARAMS_SIZE,
                                   label='params')

    @property
    @overrides(ApplicationVertex.model_name)
    def model_name(self):
        return "Munich Motor Control"

    def get_sdram_usage_for_atoms(self):
        """
        sdram calc
        :return:
        """
        return constants.SYSTEM_BYTES_REQUIREMENT + self.PARAMS_SIZE

    @staticmethod
    def get_dtcm_usage_for_atoms():
        """
        dtcm calc
        :return:
        """
        return 0

    @staticmethod
    def get_cpu_usage_for_atoms():
        """
        cpu calc
        :return:
        """
        return 0

    @overrides(AbstractVertexWithEdgeToDependentVertices.has_dependent_vertices)
    def has_dependent_vertices(self):
        """

        :return:
        """
        return True

    @overrides(AbstractVertexWithEdgeToDependentVertices.
               edge_partition_identifier_for_dependent_edge)
    def edge_partition_identifier_for_dependent_edge(self):
        """
        :return:
        """
        return MOTOR_PARTITION_ID
