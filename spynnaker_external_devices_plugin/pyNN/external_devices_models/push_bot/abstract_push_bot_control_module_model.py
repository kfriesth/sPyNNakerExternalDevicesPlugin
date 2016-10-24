from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    threshold_type_push_bot_control_module import \
    ThresholdTypePushBotControlModule

from pacman.model.constraints.key_allocator_constraints.\
    key_allocator_fixed_key_and_mask_constraint import \
    KeyAllocatorFixedKeyAndMaskConstraint
from pacman.model.decorators.overrides import overrides
from pacman.model.routing_info.base_key_and_mask import BaseKeyAndMask

from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spinn_front_end_common.utilities import exceptions

from spynnaker.pyNN.models.neuron.abstract_population_vertex \
    import AbstractPopulationVertex
from spynnaker.pyNN.models.neuron.input_types.input_type_current \
    import InputTypeCurrent
from spynnaker.pyNN.models.neuron.neuron_models\
    .neuron_model_leaky_integrate_and_fire \
    import NeuronModelLeakyIntegrateAndFire
from spynnaker.pyNN.models.neuron.synapse_types.synapse_type_exponential \
    import SynapseTypeExponential

from six import add_metaclass
from abc import ABCMeta
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


@add_metaclass(ABCMeta)
class AbstractPushBotControlModuleModel(
        AbstractPopulationVertex, AbstractProvidesOutgoingPartitionConstraints):
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
            self, n_neurons,
            # the laser
            laser_vertex,

            # the speaker
            speaker_vertex,

            # the front led
            front_led,

            # back_led
            back_led,

            # motor 0
            motor_0,

            # motor 1
            motor_1,

            # standard neuron stuff
            spikes_per_second=None, label=None,
            ring_buffer_sigma=None,
            incoming_spike_buffer_size=None, constraints=None,

            # defualt params for the neuron model type
            tau_m=default_parameters['tau_m'], cm=default_parameters['cm'],
            v_rest=default_parameters['v_rest'],
            v_reset=default_parameters['v_reset'],
            tau_syn_E=default_parameters['tau_syn_E'],
            tau_syn_I=default_parameters['tau_syn_I'],
            tau_refrac=default_parameters['tau_refrac'],
            i_offset=default_parameters['i_offset'], v_init=None,
            # global for all devices that this control module works with
            uart_id=0,
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
            led_frequency_neuron_id=None
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

        self._laser_device = laser_vertex

        self._led_device_front = front_led

        self._led_device_back = back_led

        self._motor_0 = motor_0

        self._motor_1 = motor_1

        self._speaker = speaker_vertex

        # collect keys from the different components and their command
        #  partitions
        self._partition_id_to_key = OrderedDict()

        # motor 0 stuff
        self._partition_id_to_key[self.MOTOR_0_PERMANENT_PARTITION_ID] = \
            self._motor_0.permanent_key

        self._partition_id_to_key[self.MOTOR_0_LEAKY_PARTITION_ID] = \
            self._motor_0.leaky_key

        # motor 1 stuff
        self._partition_id_to_key[self.MOTOR_1_PERMANENT_PARTITION_ID] = \
            self._motor_1.permanent_key

        self._partition_id_to_key[self.MOTOR_1_LEAKY_PARTITION_ID] = \
            self._motor_1.leaky_key

        # speaker stuff
        self._partition_id_to_key[self.SPEAKER_MELODY_PARTITION_ID] = \
            self._speaker.melody_key
        self._partition_id_to_key[self.SPEAKER_TONE_FREQUENCY_PARTITION_ID] = \
            self._speaker.frequency_key
        self._partition_id_to_key[self.SPEAKER_ACTIVE_TIME_PARTITION_ID] = \
            self._speaker.active_time_key
        self._partition_id_to_key[self.SPEAKER_TOTAL_PERIOD_PARTITION_ID] = \
            self._speaker.total_period_key

        # led device back
        self._partition_id_to_key[self.LED_BACK_FREQUENCY_PARTITION_ID] = \
            self._led_device_back.frequency_key

        self._partition_id_to_key[self.LED_BACK_ACTIVE_TIME_PARTITION_ID] = \
            self._led_device_back.active_time_key

        self._partition_id_to_key[self.LED_BACK_TOTAL_PERIOD_PARTITION_ID] = \
            self._led_device_back.total_period_key

        # led device front
        self._partition_id_to_key[self.LED_FRONT_FREQUENCY_PARTITION_ID] = \
            self._led_device_front.frequency_key

        self._partition_id_to_key[self.LED_FRONT_ACTIVE_TIME_PARTITION_ID] = \
            self._led_device_front.active_time_key

        self._partition_id_to_key[self.LED_FRONT_TOTAL_PERIOD_PARTITION_ID] = \
            self._led_device_front.total_period_key

        # laser device
        self._partition_id_to_key[self.LASER_FREQUENCY_PARTITION_ID] = \
            self._laser_device.frequency_key

        self._partition_id_to_key[self.LASER_ACTIVE_TIME_PARTITION_ID] = \
            self._laser_device.active_time_key

        self._partition_id_to_key[self.LASER_TOTAL_PERIOD_PARTITION_ID] = \
            self._laser_device.total_period_key

        # sort out neuron ids to be in a numerical order
        self._neuron_to_command_id_mapping, protocol_key_offset_mapping, \
        self._key_to_atom_map, self._atom_to_key_map = \
            self._generate_neuron_mappings(
                motor_0_permanent_velocity_neuron_id,
                motor_0_leaky_velocity_neuron_id,
                motor_1_permanent_velocity_neuron_id,
                motor_1_leaky_velocity_neuron_id, laser_total_period_neuron_id,
                speaker_total_period_neuron_id, leds_total_period_neuron_id,
                laser_active_time_neuron_id, speaker_active_time_neuron_id,
                front_led_active_time_neuron_id,
                back_led_active_time_neuron_id,
                speaker_tone_frequency_neuron_id, speaker_melody_neuron_id,
                laser_frequency_neuron_id, led_frequency_neuron_id,
                self._laser_device, self._led_device_front,
                self._led_device_back, self._motor_0, self._motor_1,
                self._speaker)

        self._uart_id = uart_id

        neuron_model = NeuronModelLeakyIntegrateAndFire(
            n_neurons, v_init, v_rest, tau_m, cm, i_offset,
            v_reset, tau_refrac)
        synapse_type = SynapseTypeExponential(
            n_neurons, tau_syn_E, tau_syn_I)
        input_type = InputTypeCurrent()
        threshold_type = ThresholdTypePushBotControlModule(
            n_neurons, uart_id, self._neuron_to_command_id_mapping,
            protocol_key_offset_mapping)

        AbstractPopulationVertex.__init__(
            self, n_neurons=n_neurons,
            binary="push_bot_spinnaker_link_control_module_n_model.aplx",
            label=label,
            max_atoms_per_core=
            AbstractPushBotControlModuleModel.
            _model_based_max_atoms_per_core,
            spikes_per_second=spikes_per_second,
            ring_buffer_sigma=ring_buffer_sigma,
            incoming_spike_buffer_size=incoming_spike_buffer_size,
            model_name="PushBotSpiNNakerLinkControlModuleNModel",
            neuron_model=neuron_model,
            input_type=input_type, synapse_type=synapse_type,
            threshold_type=threshold_type, constraints=constraints)

    def _generate_neuron_mappings(
            self, motor_0_permanent_velocity_neuron_id,
            motor_0_leaky_velocity_neuron_id,
            motor_1_permanent_velocity_neuron_id,
            motor_1_leaky_velocity_neuron_id, laser_total_period_neuron_id,
            speaker_total_period_neuron_id, leds_total_period_neuron_id,
            laser_active_time_neuron_id, speaker_active_time_neuron_id,
            front_led_active_time_neuron_id, back_led_active_time_neuron_id,
            speaker_tone_frequency_neuron_id, speaker_melody_neuron_id,
            laser_frequency_neuron_id, led_frequency_neuron_id, laser_device,
            led_device_front, led_device_back, motor_0, motor_1, speaker):

        neuron_id_to_command_id_mapping = dict()
        key_offset_map = dict()
        key_to_atom_map = dict()
        atom_to_key_map = dict()
        # go through the different possible neuron ids and build
        # corresponding mapping objects

        if motor_0_permanent_velocity_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                motor_0_permanent_velocity_neuron_id] = 1 << 0
            key_offset_map[motor_0_permanent_velocity_neuron_id] = \
                motor_0.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                self.MOTOR_0_PERMANENT_PARTITION_ID]] = \
                motor_0_permanent_velocity_neuron_id
            atom_to_key_map[motor_0_permanent_velocity_neuron_id] = \
                self._partition_id_to_key[self.MOTOR_0_PERMANENT_PARTITION_ID]

        if motor_0_leaky_velocity_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                motor_0_leaky_velocity_neuron_id] = 1 << 1
            key_offset_map[motor_0_leaky_velocity_neuron_id] = \
                motor_0.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                self.MOTOR_0_LEAKY_PARTITION_ID]] =\
                motor_0_leaky_velocity_neuron_id
            atom_to_key_map[motor_0_leaky_velocity_neuron_id] = \
                self._partition_id_to_key[self.MOTOR_0_LEAKY_PARTITION_ID]

        if motor_1_permanent_velocity_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                motor_1_permanent_velocity_neuron_id] = 1 << 2
            key_offset_map[motor_1_permanent_velocity_neuron_id] = \
                motor_1.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                self.MOTOR_1_PERMANENT_PARTITION_ID]] = \
                motor_1_permanent_velocity_neuron_id
            atom_to_key_map[motor_1_permanent_velocity_neuron_id] = \
                self._partition_id_to_key[self.MOTOR_1_PERMANENT_PARTITION_ID]

        if motor_1_leaky_velocity_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                motor_1_leaky_velocity_neuron_id] = 1 << 3
            key_offset_map[motor_1_leaky_velocity_neuron_id] = \
                motor_1.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                self.MOTOR_1_LEAKY_PARTITION_ID]] = \
                motor_1_leaky_velocity_neuron_id
            atom_to_key_map[motor_1_leaky_velocity_neuron_id] = \
                self._partition_id_to_key[self.MOTOR_1_LEAKY_PARTITION_ID]

        if laser_total_period_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                laser_total_period_neuron_id] = 1 << 4
            key_offset_map[laser_total_period_neuron_id] = \
                laser_device.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                self.LASER_TOTAL_PERIOD_PARTITION_ID]] = \
                laser_total_period_neuron_id
            atom_to_key_map[laser_total_period_neuron_id] = \
                self._partition_id_to_key[self.LASER_TOTAL_PERIOD_PARTITION_ID]

        if speaker_total_period_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                speaker_total_period_neuron_id] = 1 << 5
            key_offset_map[speaker_total_period_neuron_id] = \
                laser_device.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                    self.SPEAKER_TOTAL_PERIOD_PARTITION_ID]] =\
                speaker_total_period_neuron_id
            atom_to_key_map[speaker_total_period_neuron_id] = \
                self._partition_id_to_key[
                    self.SPEAKER_TOTAL_PERIOD_PARTITION_ID]

        if leds_total_period_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                leds_total_period_neuron_id] = 1 << 6
            key_offset_map[leds_total_period_neuron_id] = \
                led_device_back.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                    self.LED_BACK_TOTAL_PERIOD_PARTITION_ID]] = \
                leds_total_period_neuron_id
            atom_to_key_map[leds_total_period_neuron_id] = \
                self._partition_id_to_key[
                    self.LED_BACK_TOTAL_PERIOD_PARTITION_ID]

        if laser_active_time_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                laser_active_time_neuron_id] = 1 << 7
            key_offset_map[laser_active_time_neuron_id] = \
                laser_device.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                self.LASER_ACTIVE_TIME_PARTITION_ID]] = \
                laser_active_time_neuron_id
            atom_to_key_map[laser_active_time_neuron_id] = \
                self._partition_id_to_key[
                    self.LASER_ACTIVE_TIME_PARTITION_ID]

        if speaker_active_time_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                speaker_active_time_neuron_id] = 1 << 8
            key_offset_map[speaker_active_time_neuron_id] = \
                speaker.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                self.SPEAKER_ACTIVE_TIME_PARTITION_ID]] = \
                speaker_active_time_neuron_id
            atom_to_key_map[speaker_active_time_neuron_id] = \
                self._partition_id_to_key[
                    self.SPEAKER_ACTIVE_TIME_PARTITION_ID]

        if front_led_active_time_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                front_led_active_time_neuron_id] = 1 << 9
            key_offset_map[front_led_active_time_neuron_id] = \
                led_device_front.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                    self.LED_FRONT_ACTIVE_TIME_PARTITION_ID]] = \
                front_led_active_time_neuron_id
            atom_to_key_map[front_led_active_time_neuron_id] = \
                self._partition_id_to_key[
                    self.LED_FRONT_ACTIVE_TIME_PARTITION_ID]

        if back_led_active_time_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                back_led_active_time_neuron_id] = 1 << 10
            key_offset_map[back_led_active_time_neuron_id] = \
                led_device_front.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                    self.LED_BACK_ACTIVE_TIME_PARTITION_ID]] = \
                back_led_active_time_neuron_id
            atom_to_key_map[back_led_active_time_neuron_id] = \
                self._partition_id_to_key[
                    self.LED_BACK_ACTIVE_TIME_PARTITION_ID]

        if speaker_tone_frequency_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                speaker_tone_frequency_neuron_id] = 1 << 11
            key_offset_map[speaker_tone_frequency_neuron_id] = \
                speaker.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                    self.SPEAKER_TONE_FREQUENCY_PARTITION_ID]] = \
                speaker_tone_frequency_neuron_id
            atom_to_key_map[speaker_tone_frequency_neuron_id] = \
                self._partition_id_to_key[
                    self.SPEAKER_TONE_FREQUENCY_PARTITION_ID]

        if speaker_melody_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                speaker_melody_neuron_id] = 1 << 12
            key_offset_map[speaker_melody_neuron_id] = \
                speaker.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                self.SPEAKER_MELODY_PARTITION_ID]] = speaker_melody_neuron_id
            atom_to_key_map[speaker_melody_neuron_id] = \
                self._partition_id_to_key[self.SPEAKER_MELODY_PARTITION_ID]

        if led_frequency_neuron_id is not None:
            neuron_id_to_command_id_mapping[led_frequency_neuron_id] = 1 << 13
            key_offset_map[led_frequency_neuron_id] = \
                led_device_back.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                    self.LED_FRONT_FREQUENCY_PARTITION_ID]] = \
                led_frequency_neuron_id
            atom_to_key_map[led_frequency_neuron_id] = \
                self._partition_id_to_key[
                    self.LED_FRONT_FREQUENCY_PARTITION_ID]

        if laser_frequency_neuron_id is not None:
            neuron_id_to_command_id_mapping[
                laser_frequency_neuron_id] = 1 << 14
            key_offset_map[laser_frequency_neuron_id] = \
                laser_device.protocol_instance_key
            key_to_atom_map[self._partition_id_to_key[
                self.LASER_FREQUENCY_PARTITION_ID]] = laser_frequency_neuron_id
            atom_to_key_map[laser_frequency_neuron_id] = \
                self._partition_id_to_key[self.LASER_FREQUENCY_PARTITION_ID]

        return neuron_id_to_command_id_mapping, key_offset_map,\
            key_to_atom_map, atom_to_key_map

    def get_key_from_atom_mapping(self, atom_id):
        return self._atom_to_key_map[atom_id]

    def all_partition_ids(self):
        """ returns all the possible partition ids needed by the control vertex

        :return:
        """
        partitions = list()
        partitions.append(self.LASER_TOTAL_PERIOD_PARTITION_ID)
        partitions.append(self.LASER_ACTIVE_TIME_PARTITION_ID)
        partitions.append(self.LASER_FREQUENCY_PARTITION_ID)
        partitions.append(self.LED_FRONT_TOTAL_PERIOD_PARTITION_ID)
        partitions.append(self.LED_FRONT_ACTIVE_TIME_PARTITION_ID)
        partitions.append(self.LED_FRONT_FREQUENCY_PARTITION_ID)
        partitions.append(self.LED_BACK_ACTIVE_TIME_PARTITION_ID)
        partitions.append(self.MOTOR_0_PERMANENT_PARTITION_ID)
        partitions.append(self.MOTOR_0_LEAKY_PARTITION_ID)
        partitions.append(self.MOTOR_1_PERMANENT_PARTITION_ID)
        partitions.append(self.MOTOR_1_LEAKY_PARTITION_ID)
        partitions.append(self.SPEAKER_TOTAL_PERIOD_PARTITION_ID)
        partitions.append(self.SPEAKER_ACTIVE_TIME_PARTITION_ID)
        partitions.append(self.SPEAKER_TONE_FREQUENCY_PARTITION_ID)
        partitions.append(self.SPEAKER_MELODY_PARTITION_ID)
        return partitions

    @property
    def get_start_resume_commands(self):
        commands = list()
        commands.extend(self._laser_device.start_resume_commands)
        commands.extend(self._led_device_front.start_resume_commands)
        commands.extend(self._led_device_back.start_resume_commands)
        commands.extend(self._motor_0.start_resume_commands)
        commands.extend(self._motor_1.start_resume_commands)
        commands.extend(self._speaker.start_resume_commands)
        return commands

    @property
    def get_stop_pause_commands(self):
        commands = list()
        commands.extend(self._laser_device.pause_stop_commands)
        commands.extend(self._led_device_front.pause_stop_commands)
        commands.extend(self._led_device_back.pause_stop_commands)
        commands.extend(self._motor_0.pause_stop_commands)
        commands.extend(self._motor_1.pause_stop_commands)
        commands.extend(self._speaker.pause_stop_commands)
        return commands

    @staticmethod
    def set_model_max_atoms_per_core(new_value):
        AbstractPushBotControlModuleModel.\
            _model_based_max_atoms_per_core = new_value

    @property
    def uart_id(self):
        return self._uart_id

    @property
    def motor_0_leaky_command_key(self):
        return self._motor_0.leaky_key

    @property
    def motor_0_perm_command_key(self):
        return self._motor_0.permanent_key

    @property
    def motor_1_leaky_command_key(self):
        return self._motor_1.leaky_key

    @property
    def motor_1_perm_command_key(self):
        return self._motor_1.permanent_key

    @property
    def laser_config_total_period_command_key(self):
        return self._laser_device.total_period_key

    @property
    def laser_config_frequency_command_key(self):
        return self._laser_device.frequency_key

    @property
    def laser_config_active_time_command_key(self):
        return self._laser_device.active_time_key

    @property
    def led_config_total_period_command_key(self):
        return self._led_device_front.total_period_key

    @property
    def led_config_frequency_command_key(self):
        return self._led_device_front.frequency_key

    @property
    def led_config_active_time_command_key(self):
        return self._led_device_front.active_time_key

    @property
    def speaker_config_total_period_command_key(self):
        return self._speaker.total_period_key

    @property
    def speaker_set_tone_command_key(self):
        return self._speaker.frequency_key

    @property
    def speaker_config_active_time_command_key(self):
        return self._speaker.active_time_key

    @property
    def enable_motor_key(self):
        return self._motor_0.enable_motor_key

    @property
    def disable_motor_key(self):
        return self._motor_0.disable_motor_key

    @staticmethod
    def get_max_atoms_per_core():
        return AbstractPushBotControlModuleModel.\
            _model_based_max_atoms_per_core

    def routing_key_partition_atom_mapping(self, routing_info, partition):
        atom_to_key_map = list()
        key = self._partition_id_to_key[partition.identifier]
        if key in self._key_to_atom_map:
            atom_id = self._key_to_atom_map[key]
            atom_to_key_map.append((atom_id, key))
            return atom_to_key_map
        else:
            return atom_to_key_map

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
