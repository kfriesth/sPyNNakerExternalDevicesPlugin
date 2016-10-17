from pacman.model.constraints.key_allocator_constraints.\
    key_allocator_fixed_key_and_mask_constraint import \
    KeyAllocatorFixedKeyAndMaskConstraint
from pacman.model.decorators.overrides import overrides
from pacman.model.routing_info.base_key_and_mask import BaseKeyAndMask
from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spinn_front_end_common.abstract_models.impl.\
    vertex_with_dependent_vertices import \
    VertexWithEdgeToDependentVertices
from spynnaker.pyNN.models.neuron.neuron_models\
    .neuron_model_leaky_integrate_and_fire \
    import NeuronModelLeakyIntegrateAndFire
from spynnaker.pyNN.models.neuron.synapse_types.synapse_type_exponential \
    import SynapseTypeExponential
from spynnaker.pyNN.models.neuron.input_types.input_type_current \
    import InputTypeCurrent
from spynnaker.pyNN.models.neuron.abstract_population_vertex \
    import AbstractPopulationVertex
from spynnaker_external_devices_plugin.pyNN import \
    PushBotSpiNNakerLinkMotorDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link_laser_device import \
    PushBotSpiNNakerLinkLaserDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link_led_device import \
    PushBotSpiNNakerLinkLEDDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link_speaker_device import \
    PushBotSpiNNakerLinkSpeakerDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    threshold_type_push_bot_control_module import \
    ThresholdTypePushBotControlModule
from spinn_front_end_common.utilities import exceptions

import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class PushBotSpinnakerLinkControlModuleNModel(
        AbstractPopulationVertex, VertexWithEdgeToDependentVertices,
        AbstractProvidesOutgoingPartitionConstraints):
    """ Leaky integrate and fire neuron with an exponentially decaying \
        current input
    """

    _model_based_max_atoms_per_core = 15

    default_parameters = {
        'tau_m': 20.0, 'cm': 1.0, 'v_rest': 0.0, 'v_reset': 0.0,
        'tau_syn_E': 5.0, 'tau_syn_I': 5.0, 'tau_refrac': 0.1, 'i_offset': 0}

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

    def __init__(
            self, n_neurons, spinnaker_link_id, spikes_per_second=None,
            ring_buffer_sigma=None,
            incoming_spike_buffer_size=None, constraints=None, label=None,

            # defualt params for the neuron model type
            tau_m=default_parameters['tau_m'], cm=default_parameters['cm'],
            v_rest=default_parameters['v_rest'],
            v_reset=default_parameters['v_reset'],
            tau_syn_E=default_parameters['tau_syn_E'],
            tau_syn_I=default_parameters['tau_syn_I'],
            tau_refrac=default_parameters['tau_refrac'],
            i_offset=default_parameters['i_offset'], v_init=None,
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
            speaker_start_frequency=None, speaker_melody_value=None,
            # neuron_ids for devices
            motor_0_permanent_velocity_neuron_id=None,
            motor_0_leaky_velocity_neuron_id=None,
            motor_1_permanent_velocity_neuron_id=None,
            motor_1_leaky_velocity_neuron_id=None,
            laser_total_period_neuron_id=None,
            speaker_total_period_neuron_id=None,
            leds_total_period_neuron_id=None,
            laser_active_time_neuron_id=None,
            speaker_active_time_neuron_id=None,
            front_led_active_time_neuron_id=None,
            back_led_active_time_neuron_id=None,
            speaker_tone_frequency_neuron_id=None,
            speaker_melody_neuron_id=None,
            laser_frequency_neuron_id=None,
            led_frequency_neuron_id = None
    ):
        label = "PushBotControlModule"
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

        # verify that only 0 or one of mutually exclusive commands is set
        if ((motor_0_permanent_velocity_neuron_id is not None and
                motor_0_leaky_velocity_neuron_id is not None) or
                (motor_1_permanent_velocity_neuron_id is not None and
                 motor_1_leaky_velocity_neuron_id is not None) or
                (speaker_tone_frequency_neuron_id is not None and
                 speaker_melody_neuron_id is not None)):
            raise exceptions.ConfigurationException(
                "Only 1 neuron can be allocated to a command, or to a motor, "
                "or to control the tone/melody of the speaker.")

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

        # collect keys from the different components and their command
        #  partitions
        self._partition_id_to_key = OrderedDict()

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

        # speaker stuff
        self._partition_id_to_key[self.SPEAKER_MELODY_PARTITION_ID] = \
            speaker.melody_key
        self._partition_id_to_key[self.SPEAKER_TONE_FREQUENCY_PARTITION_ID] = \
            speaker.frequency_key
        self._partition_id_to_key[self.SPEAKER_ACTIVE_TIME_PARTITION_ID] = \
            speaker.active_time_key
        self._partition_id_to_key[self.SPEAKER_TOTAL_PERIOD_PARTITION_ID] = \
            speaker.total_period_key

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

        # sort out neuron ids to be in a numerical order
        mapping, protocol_key_offset_mapping = self._generate_neuron_mapping(
            motor_0_permanent_velocity_neuron_id,
            motor_0_leaky_velocity_neuron_id,
            motor_1_permanent_velocity_neuron_id,
            motor_1_leaky_velocity_neuron_id, laser_total_period_neuron_id,
            speaker_total_period_neuron_id, leds_total_period_neuron_id,
            laser_active_time_neuron_id, speaker_active_time_neuron_id,
            front_led_active_time_neuron_id, back_led_active_time_neuron_id,
            speaker_tone_frequency_neuron_id, speaker_melody_neuron_id,
            laser_frequency_neuron_id, led_frequency_neuron_id, laser_device,
            led_device_front, led_device_back, motor_0, motor_1, speaker)

        neuron_model = NeuronModelLeakyIntegrateAndFire(
            n_neurons, v_init, v_rest, tau_m, cm, i_offset,
            v_reset, tau_refrac)
        synapse_type = SynapseTypeExponential(
            n_neurons, tau_syn_E, tau_syn_I)
        input_type = InputTypeCurrent()
        threshold_type = ThresholdTypePushBotControlModule(
            n_neurons, uart_id, mapping, protocol_key_offset_mapping)

        AbstractPopulationVertex.__init__(
            self, n_neurons=n_neurons,
            binary="push_bot_spinnaker_link_control_module_n_model.aplx",
            label=label,
            max_atoms_per_core=
            PushBotSpinnakerLinkControlModuleNModel.
            _model_based_max_atoms_per_core,
            spikes_per_second=spikes_per_second,
            ring_buffer_sigma=ring_buffer_sigma,
            incoming_spike_buffer_size=incoming_spike_buffer_size,
            model_name="PushBotSpiNNakerLinkControlModuleNModel",
            neuron_model=neuron_model,
            input_type=input_type, synapse_type=synapse_type,
            threshold_type=threshold_type, constraints=constraints)

    def _generate_neuron_mapping(self, motor_0_permanent_velocity_neuron_id,
            motor_0_leaky_velocity_neuron_id,
            motor_1_permanent_velocity_neuron_id,
            motor_1_leaky_velocity_neuron_id, laser_total_period_neuron_id,
            speaker_total_period_neuron_id, leds_total_period_neuron_id,
            laser_active_time_neuron_id, speaker_active_time_neuron_id,
            front_led_active_time_neuron_id, back_led_active_time_neuron_id,
            speaker_tone_frequency_neuron_id, speaker_melody_neuron_id,
            laser_frequency_neuron_id, led_frequency_neuron_id,
            laser_device, led_device_front, led_device_back, motor_0, motor_1,
            speaker):

        mapping = dict()
        key_offset_map = dict()

        if motor_0_permanent_velocity_neuron_id is not None:
            mapping[motor_0_permanent_velocity_neuron_id] = 1 << 0
            key_offset_map[motor_0_permanent_velocity_neuron_id] = \
                motor_0.protocol_instance_key
        if motor_0_leaky_velocity_neuron_id is not None:
            mapping[motor_0_leaky_velocity_neuron_id] = 1 << 1
            key_offset_map[motor_0_leaky_velocity_neuron_id] = \
                motor_0.protocol_instance_key
        if motor_1_permanent_velocity_neuron_id is not None:
            mapping[motor_1_permanent_velocity_neuron_id] = 1 << 2
            key_offset_map[motor_1_permanent_velocity_neuron_id] = \
                motor_1.protocol_instance_key
        if motor_1_leaky_velocity_neuron_id is not None:
            mapping[motor_1_leaky_velocity_neuron_id] = 1 << 3
            key_offset_map[motor_1_leaky_velocity_neuron_id] = \
                motor_1.protocol_instance_key
        if laser_total_period_neuron_id is not None:
            mapping[laser_total_period_neuron_id] = 1 << 4
            key_offset_map[laser_total_period_neuron_id] = \
                laser_device.protocol_instance_key
        if speaker_total_period_neuron_id is not None:
            mapping[speaker_total_period_neuron_id] = 1 << 5
            key_offset_map[speaker_total_period_neuron_id] = \
                laser_device.protocol_instance_key
        if leds_total_period_neuron_id is not None:
            mapping[leds_total_period_neuron_id] = 1 << 6
            key_offset_map[leds_total_period_neuron_id] = \
                led_device_back.protocol_instance_key
        if laser_active_time_neuron_id is not None:
            mapping[laser_active_time_neuron_id] = 1 << 7
            key_offset_map[laser_active_time_neuron_id] = \
                laser_device.protocol_instance_key
        if speaker_active_time_neuron_id is not None:
            mapping[speaker_active_time_neuron_id] = 1 << 8
            key_offset_map[speaker_active_time_neuron_id] = \
                speaker.protocol_instance_key
        if front_led_active_time_neuron_id is not None:
            mapping[front_led_active_time_neuron_id] = 1 << 9
            key_offset_map[front_led_active_time_neuron_id] = \
                led_device_front.protocol_instance_key
        if back_led_active_time_neuron_id is not None:
            mapping[back_led_active_time_neuron_id] = 1 << 10
            key_offset_map[back_led_active_time_neuron_id] = \
                led_device_front.protocol_instance_key
        if speaker_tone_frequency_neuron_id is not None:
            mapping[speaker_tone_frequency_neuron_id] = 1 << 11
            key_offset_map[speaker_tone_frequency_neuron_id] = \
                speaker.protocol_instance_key
        if speaker_melody_neuron_id is not None:
            mapping[speaker_melody_neuron_id] = 1 << 12
            key_offset_map[speaker_melody_neuron_id] = \
                speaker.protocol_instance_key
        if led_frequency_neuron_id is not None:
            mapping[led_frequency_neuron_id] = 1 << 13
            key_offset_map[led_frequency_neuron_id] = \
                led_device_back.protocol_instance_key
        if laser_frequency_neuron_id is not None:
            mapping[laser_frequency_neuron_id] = 1 << 14
            key_offset_map[laser_frequency_neuron_id] = \
                laser_device.protocol_instance_key

        return mapping, key_offset_map

    @staticmethod
    def set_model_max_atoms_per_core(new_value):
        PushBotSpinnakerLinkControlModuleNModel.\
            _model_based_max_atoms_per_core = new_value

    @staticmethod
    def get_max_atoms_per_core():
        return PushBotSpinnakerLinkControlModuleNModel.\
            _model_based_max_atoms_per_core

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
