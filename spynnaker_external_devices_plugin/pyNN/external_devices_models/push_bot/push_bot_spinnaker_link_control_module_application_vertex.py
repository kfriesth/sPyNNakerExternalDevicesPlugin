# pacman imports
from pacman.model.constraints.key_allocator_constraints.\
    key_allocator_fixed_key_and_mask_constraint import \
    KeyAllocatorFixedKeyAndMaskConstraint
from pacman.model.decorators.overrides import overrides
from pacman.model.graphs.application.impl.application_vertex import \
    ApplicationVertex
from pacman.model.resources.cpu_cycles_per_tick_resource import \
    CPUCyclesPerTickResource
from pacman.model.resources.dtcm_resource import DTCMResource
from pacman.model.resources.resource_container import ResourceContainer
from pacman.model.resources.sdram_resource import SDRAMResource
from pacman.model.routing_info.base_key_and_mask import BaseKeyAndMask

# spinn front end common imports
from spinn_front_end_common.abstract_models.\
    abstract_binary_uses_simulation_run import \
    AbstractBinaryUsesSimulationRun
from spinn_front_end_common.abstract_models.\
    abstract_has_associated_binary import \
    AbstractHasAssociatedBinary
from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spinn_front_end_common.abstract_models.impl.\
    application_data_specable_vertex import \
    ApplicationDataSpecableVertex
from spinn_front_end_common.abstract_models.impl.\
    vertex_with_dependent_vertices import \
    VertexWithEdgeToDependentVertices
from spinn_front_end_common.utilities import constants
from spinn_front_end_common.utilities import exceptions

# external devices plugin imports
from spynnaker.pyNN.models.abstract_models.abstract_contains_a_synaptic_manager import \
    AbstractContainsASynapticManager
from spynnaker.pyNN.models.neuron.synapse_types.synapse_type_exponential import \
    SynapseTypeExponential
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link_control_module_machine_vertex import \
    PushBotSpiNNakerLinkControlModuleMachineVertex
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link_laser_device import PushBotSpiNNakerLinkLaserDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link_motor_device import PushBotSpiNNakerLinkMotorDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link_led_device import PushBotSpiNNakerLinkLEDDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link_speaker_device \
    import PushBotSpiNNakerLinkSpeakerDevice

import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class PushBotSpiNNakerLinkControlModuleApplicationVertex(
        ApplicationDataSpecableVertex, AbstractHasAssociatedBinary,
        ApplicationVertex, VertexWithEdgeToDependentVertices,
        AbstractProvidesOutgoingPartitionConstraints,
        AbstractBinaryUsesSimulationRun, AbstractContainsASynapticManager):
    """ The control module class for all components of the push bot which only
    take commands, and do not generate data back to the neural network.

    """

    # all commands will use this mask
    _DEFAULT_COMMAND_MASK = 0xFFFFFFFF
    _N_NEURONS = 15

    LASER_TOTAL_PERIOD_PARTITION_ID = "Laser_total_period_partition_id"
    LASER_ACTIVE_TIME_PARTITION_ID = "Laser_active_time_partition_id"
    LASER_FREQUENCY_PARTITION_ID = "Laser_frequency_partition_id"

    LED_FRONT_TOTAL_PERIOD_PARTITION_ID = "led_front_total_period_partition_id"
    LED_FRONT_ACTIVE_TIME_PARTITION_ID = "led_front_active_time_partition_id"
    LED_FRONT_FREQUENCY_PARTITION_ID = "led_front_frequency_partition_id"

    LED_BACK_TOTAL_PERIOD_PARTITION_ID = "led_back_total_period_partition_id"
    LED_BACK_ACTIVE_TIME_PARTITION_ID = "led_back_active_time_partition_id"
    LED_BACK_FREQUENCY_PARTITION_ID = "led_back_frequency_partition_id"

    MOTOR_0_PERMANENT_PARTITION_ID = "motor_0_permanent_partition_id"
    MOTOR_0_LEAKY_PARTITION_ID = "motor_0_leaking_towards_zero_partition_id"
    MOTOR_1_PERMANENT_PARTITION_ID = "motor_1_permanent_partition_id"
    MOTOR_1_LEAKY_PARTITION_ID = "motor_1_leaking_towards_zero_partition_id"

    SPEAKER_TOTAL_PERIOD_PARTITION_ID = "Speaker_total_period_partition_id"
    SPEAKER_ACTIVE_TIME_PARTITION_ID = "Speaker_active_time_partition_id"
    SPEAKER_TONE_FREQUENCY_PARTITION_ID = "Speaker_tone_set_partition_id"
    SPEAKER_MELODY_PARTITION_ID = "Speaker_melody_partition_id"

    warning_message = \
        "The control module must have only 15 neurons. The relationship " \
        "between each neuron and its corresponding external device is as " \
        "follows:\n\n" \
        "0: at next timer tick the motor command is motor 0 permanent " \
        "velocity. The velocity is deduced from the number of packets " \
        "received by this neuron\n" \
        "1: at next timer tick the motor command is motor 0 leaky velocity. " \
        "The velocity is deduced from the number of packets received by " \
        "this neuron\n"\
        "2: at next timer tick the motor command is motor 1 permanent " \
        "velocity. The velocity is deduced from the number of packets " \
        "received by this neuron\n" \
        "3: at next timer tick the motor command is motor 1 leaky velocity. " \
        "The velocity is deduced from the number of packets received by this " \
        "neuron\n"\
        "4: at next timer tick, the laser total period will be set to the " \
        "number of packets received by this neuron. \n"\
        "5: at next timer tick, the speaker total period will be set to the " \
        "number of packets received by this neuron. \n" \
        "6: at the next timer tick, the leds total period will be set to " \
        "the number of packets received by this neuron. \n" \
        "7: at the next timer tick, the laser active timer will be set to " \
        "the number of packets received by this neuron. \n " \
        "8: at the next timer tick, the speaker active timer will be set to " \
        "the number of packets received by this neuron. \n" \
        "9: at the next timer tick, the front led active timer will be set " \
        "to the number of packets received by this neuron. \n" \
        "10: at the next timer tick, the back led active timer will be set " \
        "to the number of packets received by this neuron. \n" \
        "11: at the next timer tick, the speaker tone frequency will be set " \
        "to the number of packets received by this neuron. \n" \
        "12: at the next timer tick, the speaker will play melody that is " \
        "set by the number of packets received by this neuron" \
        "13: at the next timer tick, the led frequency will be set to the " \
        "number of packets received by this neuron. \n" \
        "14: at the next timer tick, the laser frequency will be set to the " \
        "number of packets received by this neuron. \n" \
        "at each timer tick, only one of these sets should be active:" \
        " [0,1,2,3], [11, 12] "

    def __init__(
            self, n_neurons, label, spinnaker_link_id,
            # global for all devices that this control module works with
            board_address=None, uart_id=0,
            # the laser bespoke setup params
            laser_start_active_time=0, laser_start_total_period=0,
            laser_start_frequency=0,
            # the front led bespoke setup params
            front_led_start_active_time=0,
            front_led_total_period=0, front_led_start_frequency=0,
            # the back led bespoke setup params
            back_led_start_active_time=0,
            back_led_total_period=0, back_led_start_frequency=0,
            # the speaker bespoke setup params
            speaker_start_active_time=0, speaker_start_total_period=0,
            speaker_start_frequency=None, speaker_melody_value=None):
        """

        :param n_neurons:
        :param label:
        :param spinnaker_link_id:
        :param board_address:
        :param uart_id:
        :param laser_start_active_time:
        :param laser_start_total_period:
        :param laser_start_frequency:
        :param front_led_start_active_time:
        :param front_led_total_period:
        :param front_led_start_frequency:
        :param back_led_start_active_time:
        :param back_led_total_period:
        :param back_led_start_frequency:
        :param speaker_start_active_time:
        :param speaker_start_total_period:
        :param speaker_start_frequency:
        :param speaker_melody_value:
        """

        # set up inheritance
        ApplicationVertex.__init__(self, label)
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)
        AbstractHasAssociatedBinary.__init__(self)
        ApplicationDataSpecableVertex.__init__(self)
        AbstractBinaryUsesSimulationRun.__init__(self)
        AbstractContainsASynapticManager.__init__(
            self, synapse_type=SynapseTypeExponential(self._N_NEURONS, 0, 0),
            ring_buffer_sigma=None, spikes_per_second=None)

        laser_device = PushBotSpiNNakerLinkLaserDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, start_active_time=laser_start_active_time,
            start_total_period=laser_start_total_period,
            start_frequency=laser_start_frequency, label="the push bot laser")

        led_device_front = PushBotSpiNNakerLinkLEDDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, start_active_time=front_led_start_active_time,
            front_led=True, start_total_period=front_led_total_period,
            start_frequency=front_led_start_frequency,
            label="the push bot front led")

        led_device_back = PushBotSpiNNakerLinkLEDDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, start_active_time=back_led_start_active_time,
            front_led=False, start_total_period=back_led_total_period,
            start_frequency=back_led_start_frequency,
            label="The push bot back led")

        motor_0 = PushBotSpiNNakerLinkMotorDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, motor_id=0, label="The push bot first motor")

        motor_1 = PushBotSpiNNakerLinkMotorDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, motor_id=1, label="The push bot second motor")

        speaker = PushBotSpiNNakerLinkSpeakerDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            start_active_time=speaker_start_active_time,
            start_total_period=speaker_start_total_period,
            start_frequency=speaker_start_frequency,
            melody_value=speaker_melody_value, label="The push bot speaker")

        VertexWithEdgeToDependentVertices.__init__(
            self,
            {laser_device: [self.LASER_TOTAL_PERIOD_PARTITION_ID,
                            self.LASER_ACTIVE_TIME_PARTITION_ID,
                            self.LASER_FREQUENCY_PARTITION_ID],
             led_device_front: [self.LED_FRONT_TOTAL_PERIOD_PARTITION_ID,
                                self.LED_FRONT_ACTIVE_TIME_PARTITION_ID,
                                self.LED_FRONT_FREQUENCY_PARTITION_ID],
             led_device_back: [self.LED_BACK_ACTIVE_TIME_PARTITION_ID],
             motor_0: [self.MOTOR_0_PERMANENT_PARTITION_ID,
                       self.MOTOR_0_LEAKY_PARTITION_ID],
             motor_1: [self.MOTOR_1_PERMANENT_PARTITION_ID,
                       self.MOTOR_1_LEAKY_PARTITION_ID],
             speaker: [self.SPEAKER_TOTAL_PERIOD_PARTITION_ID,
                       self.SPEAKER_ACTIVE_TIME_PARTITION_ID,
                       self.SPEAKER_TONE_FREQUENCY_PARTITION_ID,
                       self.SPEAKER_MELODY_PARTITION_ID]})

        if n_neurons != self._N_NEURONS:
            raise exceptions.ConfigurationException(self.warning_message)
        else:
            logger.warn(self.warning_message)

        # collect keys from the different components and their command
        #  partitions
        self._partition_id_to_key = OrderedDict()

        # speaker stuff
        self._partition_id_to_key[self.SPEAKER_MELODY_PARTITION_ID] = \
            speaker.melody_key
        self._partition_id_to_key[self.SPEAKER_TONE_FREQUENCY_PARTITION_ID] = \
            speaker.frequency_key
        self._partition_id_to_key[self.SPEAKER_ACTIVE_TIME_PARTITION_ID] = \
            speaker.active_time_key
        self._partition_id_to_key[self.SPEAKER_TOTAL_PERIOD_PARTITION_ID] = \
            speaker.total_period_key

        # motor 0 stuff
        self._partition_id_to_key[self.MOTOR_0_PERMANENT_PARTITION_ID] = \
            motor_0.permanent_key

        self._partition_id_to_key[self.MOTOR_0_LEAKY_PARTITION_ID] = \
            motor_0.leaky_key

        # motor 1 stuff
        self._partition_id_to_key[self.MOTOR_1_PERMANENT_PARTITION_ID] = \
            motor_1.permanent_key

        self._partition_id_to_key[self.MOTOR_1_LEAKY_PARTITION_ID] = \
            motor_1.leaky_key

        # led device back
        self._partition_id_to_key[self.LED_BACK_FREQUENCY_PARTITION_ID] = \
            led_device_back.frequency_key

        self._partition_id_to_key[self.LED_BACK_ACTIVE_TIME_PARTITION_ID] = \
            led_device_back.active_time_key

        self._partition_id_to_key[self.LED_BACK_TOTAL_PERIOD_PARTITION_ID] = \
            led_device_back.total_period_key

        # led device front
        self._partition_id_to_key[self.LED_FRONT_FREQUENCY_PARTITION_ID] = \
            led_device_front.frequency_key

        self._partition_id_to_key[self.LED_FRONT_ACTIVE_TIME_PARTITION_ID] = \
            led_device_front.active_time_key

        self._partition_id_to_key[self.LED_FRONT_TOTAL_PERIOD_PARTITION_ID] = \
            led_device_front.total_period_key

        # laser device
        self._partition_id_to_key[self.LASER_FREQUENCY_PARTITION_ID] = \
            laser_device.frequency_key

        self._partition_id_to_key[self.LASER_ACTIVE_TIME_PARTITION_ID] = \
            laser_device.active_time_key

        self._partition_id_to_key[self.LASER_TOTAL_PERIOD_PARTITION_ID] = \
            laser_device.total_period_key

    @property
    @overrides(ApplicationVertex.n_atoms)
    def n_atoms(self):
        return self._N_NEURONS

    @overrides(ApplicationDataSpecableVertex.
               generate_application_data_specification)
    def generate_application_data_specification(
            self, spec, placement, graph_mapper, application_graph,
            machine_graph, routing_info, iptags, reverse_iptags,
            machine_time_step, time_scale_factor):
        placement.vertex.generate_data_specification(
            spec, placement, machine_time_step, time_scale_factor,
            machine_graph, application_graph, routing_info, graph_mapper)

    @overrides(ApplicationVertex.get_resources_used_by_atoms)
    def get_resources_used_by_atoms(self, vertex_slice):
        return ResourceContainer(sdram=SDRAMResource(
            sdram=(constants.SYSTEM_BYTES_REQUIREMENT +
                   PushBotSpiNNakerLinkControlModuleMachineVertex.
                   N_KEYS_REGION_SIZE +
                   PushBotSpiNNakerLinkControlModuleMachineVertex.
                   get_provenance_data_size(0) +
                   (PushBotSpiNNakerLinkControlModuleMachineVertex.
                    TOTAL_REQUIRED_MALLOCS *
                    constants.SARK_PER_MALLOC_SDRAM_USAGE))),
            dtcm=DTCMResource(dtcm=500),
            cpu_cycles=CPUCyclesPerTickResource(500))

    @overrides(ApplicationVertex.create_machine_vertex)
    def create_machine_vertex(self, vertex_slice, resources_required,
                              label=None, constraints=None):
        return PushBotSpiNNakerLinkControlModuleMachineVertex(
            resources_required, constraints, label, self._partition_id_to_key,
            self._synapse_manager, vertex_slice)

    @overrides(AbstractProvidesOutgoingPartitionConstraints.
               get_outgoing_partition_constraints)
    def get_outgoing_partition_constraints(self, partition):
        constraints = list()
        constraints.append(
            KeyAllocatorFixedKeyAndMaskConstraint(
                [BaseKeyAndMask(
                    self._partition_id_to_key[partition.identifier],
                    self._DEFAULT_COMMAND_MASK)]))
        return constraints

    @overrides(AbstractHasAssociatedBinary.get_binary_file_name)
    def get_binary_file_name(self):
        return PushBotSpiNNakerLinkControlModuleMachineVertex.\
            get_binary_file_name()
