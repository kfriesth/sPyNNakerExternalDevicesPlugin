from collections import namedtuple
from enum import Enum, IntEnum

from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spynnaker.pyNN.models.abstract_models\
    .abstract_send_me_multicast_commands_vertex \
    import AbstractSendMeMulticastCommandsVertex
from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_fixed_key_and_mask_constraint \
    import KeyAllocatorFixedKeyAndMaskConstraint
from spynnaker.pyNN import exceptions
from pacman.model.abstract_classes.abstract_virtual_vertex import \
    AbstractVirtualVertex
from pacman.model.routing_info.base_key_and_mask import BaseKeyAndMask
from spynnaker.pyNN.utilities.multi_cast_command import MultiCastCommand


# Named tuple bundling together configuration elements of a pushbot resolution
# config
PushBotRetinaResolutionConfig = namedtuple("PushBotRetinaResolution",
                                           ["pixels", "enable_command",
                                            "coordinate_bits"])

PushBotRetinaResolution = Enum(
    value="PushBotRetinaResolution",
    names=[("Native128", PushBotRetinaResolutionConfig(128, (1 << 26), 7)),
           ("Downsample64", PushBotRetinaResolutionConfig(64, (2 << 26), 6)),
           ("Downsample32", PushBotRetinaResolutionConfig(32, (3 << 26), 5)),
           ("Downsample16", PushBotRetinaResolutionConfig(16, (4 << 26), 4))])

PushBotRetinaPolarity = IntEnum(
    value="PushBotRetinaPolarity",
    names=["Up", "Down", "Merged"])


class PushBotRetinaDevice(AbstractVirtualVertex,
                          AbstractSendMeMulticastCommandsVertex,
                          AbstractProvidesOutgoingPartitionConstraints):

    # Mask for all SpiNNaker->Pushbot commands
    MANAGEMENT_MASK = 0xFFFFF800

    # Retina-specific commands
    RETINA_ENABLE = 0x1
    RETINA_DISABLE = 0x0
    RETINA_KEY_SET = 0x2
    RETINA_NO_TIMESTAMP = (0 << 29)

    # Sensor commands
    SENSOR = 0x7F0
    SENSOR_SET_KEY = 0x0
    SENSOR_SET_PUSHBOT = 0x1

    DEFAULT_FIXED_MASK = 0xFFFF8000

    population_parameters = {'spinnaker_link', 'fixed_key', 'resolution'}

    model_name = "pushbot retina device"

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
            self, bag_of_neurons, label=None, constraints=None):
        """
            self, fixed_key, spinnaker_link_id, machine_time_step,
                 timescale_factor, label=None, n_neurons=None,
                 polarity=PushBotRetinaPolarity.Merged,
                 resolution=PushBotRetinaResolution.Downsample64):
        """

        self._bag_of_neurons = bag_of_neurons

        # assume fixed key is same for all atoms (as pop scoped)
        fixed_key = bag_of_neurons[0].get_population_parameter('fixed_key')

        # assume resolution is same for all atoms (as pop scoped)
        resolution = bag_of_neurons[0].get_population_parameter('resolution')

        # assume retina key is same for all atoms (as pop scoped)
        spinnaker_link_id = bag_of_neurons[0].get_population_parameter(
            'spinnaker_link_id')

        if not isinstance(resolution, PushBotRetinaResolution):
            raise exceptions.SpynnakerException(
                "Pushbot retina resolution should be one of those defined in"
                " Resolution enumeration")

        # Cache resolution
        self._resolution = resolution

        # Calculate number of neurons
        fixed_n_neurons = (resolution.value.pixels ** 2) * 2

        # Build routing mask
        mask_bits = (2 * resolution.value.coordinate_bits) + 1
        self._routing_mask = ~((1 << mask_bits) - 1) & 0xFFFFFFFF

        AbstractVirtualVertex.__init__(
            self, fixed_n_neurons, spinnaker_link_id,
            max_atoms_per_core=fixed_n_neurons, label=label,
            constraints=constraints)
        AbstractSendMeMulticastCommandsVertex.__init__(
            self, self._get_commands())
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

        if len(bag_of_neurons) != fixed_n_neurons:
            print "Warning, the retina will have {} neurons".format(
                len(bag_of_neurons))

    def get_outgoing_partition_constraints(self, partition, graph_mapper):
        # assume fixed key is same for all atoms (as pop scoped)
        fixed_key = \
            self._bag_of_neurons[0].get_population_parameter('fixed_key')
        return [KeyAllocatorFixedKeyAndMaskConstraint(
            [BaseKeyAndMask(fixed_key, self._routing_mask)])]

    def _get_commands(self):
        """
        method that returns the commands for the retina external device
        """
        # Set sensor key
        commands = list()

        # get fixed key
        fixed_key = \
            self._bag_of_neurons[0].get_population_parameter('fixed_key')

        commands.append(MultiCastCommand(
            0, PushBotRetinaDevice.SENSOR | PushBotRetinaDevice.SENSOR_SET_KEY,
            PushBotRetinaDevice.MANAGEMENT_MASK, fixed_key, 1, 100))

        # Set sensor to pushbot
        commands.append(MultiCastCommand(
            0, (PushBotRetinaDevice.SENSOR |
                PushBotRetinaDevice.SENSOR_SET_PUSHBOT),
            PushBotRetinaDevice.MANAGEMENT_MASK, 1,
            1, 100))

        # Ensure retina is disabled
        commands.append(MultiCastCommand(
            0, PushBotRetinaDevice.RETINA_DISABLE,
            PushBotRetinaDevice.MANAGEMENT_MASK, 0,
            1, 100))

        # Set retina key
        commands.append(MultiCastCommand(
            0, PushBotRetinaDevice.RETINA_KEY_SET,
            PushBotRetinaDevice.MANAGEMENT_MASK, fixed_key, 1, 100))

        # Enable retina
        commands.append(MultiCastCommand(
            0, PushBotRetinaDevice.RETINA_ENABLE,
            PushBotRetinaDevice.MANAGEMENT_MASK,
            (PushBotRetinaDevice.RETINA_NO_TIMESTAMP +
             self._resolution.value.enable_command),
            1, 100))

        # At end of simulation, disable retina
        commands.append(MultiCastCommand(
            -1, PushBotRetinaDevice.RETINA_DISABLE,
            PushBotRetinaDevice.MANAGEMENT_MASK, 0,
            1, 100))

        return commands

    def recieves_multicast_commands(self):
        return True

    def is_virtual_vertex(self):
        return True
