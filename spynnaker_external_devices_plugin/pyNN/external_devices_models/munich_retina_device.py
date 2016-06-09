from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spynnaker.pyNN.models.abstract_models\
    .abstract_send_me_multicast_commands_vertex \
    import AbstractSendMeMulticastCommandsVertex
from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_fixed_key_and_mask_constraint \
    import KeyAllocatorFixedKeyAndMaskConstraint
from pacman.model.abstract_classes.abstract_virtual_vertex \
    import AbstractVirtualVertex
from spynnaker.pyNN import exceptions

from pacman.model.routing_info.base_key_and_mask import BaseKeyAndMask
from spynnaker.pyNN.utilities.multi_cast_command import MultiCastCommand


# robot with 7 7 1
def get_x_from_robot_retina(key):
    return (key >> 7) & 0x7f


def get_y_from_robot_retina(key):
    return key & 0x7f


def get_spike_value_from_robot_retina(key):
    return (key >> 14) & 0x1


class MunichRetinaDevice(
        AbstractVirtualVertex, AbstractSendMeMulticastCommandsVertex,
        AbstractProvidesOutgoingPartitionConstraints):

    # key codes for the robot retina
    MANAGEMENT_BIT = 0x400
    MANAGEMENT_MASK = 0xFFFFF800
    LEFT_RETINA_ENABLE = 0x45
    RIGHT_RETINA_ENABLE = 0x46
    LEFT_RETINA_DISABLE = 0x45
    RIGHT_RETINA_DISABLE = 0x46
    LEFT_RETINA_KEY_SET = 0x43
    RIGHT_RETINA_KEY_SET = 0x44

    UP_POLARITY = "UP"
    DOWN_POLARITY = "DOWN"
    MERGED_POLARITY = "MERGED"

    LEFT_RETINA = "LEFT"
    RIGHT_RETINA = "RIGHT"

    DEFAULT_FIXED_MASK = 0xFFFF8000

    population_parameters = {
        'spinnaker_link', 'polarity', 'retina_key', 'position'}

    model_name = "external retina device"

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

        label = "external retina device at _position {} and _polarity {}"\
            .format(self._position, self._polarity)

        # assume polarity is same for all atoms (as pop scoped)
        polarity = bag_of_neurons[0].get_population_parameter('polarity')

        # assume retina key is same for all atoms (as pop scoped)
        retina_key = bag_of_neurons[0].get_population_parameter('retina_key')

        # assume polarity is same for all atoms (as pop scoped)
        position = bag_of_neurons[0].get_population_parameter('position')

        # check position is valid
        if position != self.RIGHT_RETINA and position != self.LEFT_RETINA:
            raise exceptions.SpynnakerException(
                "The external Retina does not recognise this _position")

        # assume retina key is same for all atoms (as pop scoped)
        spinnaker_link_id = bag_of_neurons[0].get_population_parameter(
            'spinnaker_link_id')

        if polarity is None:
            polarity = MunichRetinaDevice.MERGED_POLARITY

        # update retina key
        retina_key = (retina_key & 0xFFFF) << 16
        if polarity == MunichRetinaDevice.UP_POLARITY:
            retina_key |= 0x4000

        # update all atoms with new fixed_key
        for atom in bag_of_neurons:
            atom.set_population_parameter('retina_key', retina_key)

        self._fixed_mask = MunichRetinaDevice.DEFAULT_FIXED_MASK
        if polarity == MunichRetinaDevice.MERGED_POLARITY:

            # There are 128 x 128 retina "pixels" x 2 polarities
            fixed_n_neurons = 128 * 128 * 2
        else:

            # There are 128 x 128 retina "pixels"
            fixed_n_neurons = 128 * 128
            self._fixed_mask = 0xFFFFC000

        if len(bag_of_neurons) != fixed_n_neurons:
            print "Warning, the retina will have {} neurons"\
                .format(len(bag_of_neurons))

        AbstractVirtualVertex.__init__(
            self, fixed_n_neurons, spinnaker_link_id,
            max_atoms_per_core=fixed_n_neurons, label=label)
        AbstractSendMeMulticastCommandsVertex.__init__(
            self, self._get_commands(position))
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

    def get_outgoing_partition_constraints(self, partition, graph_mapper):
        return [KeyAllocatorFixedKeyAndMaskConstraint(
            [BaseKeyAndMask(self._fixed_key, self._fixed_mask)])]

    def _get_commands(self, position):
        """ Return the commands for the retina external device
        """
        commands = list()

        # change the retina key it transmits with
        # (based off if its right or left)
        if position == self.RIGHT_RETINA:
            key_set_command = self.MANAGEMENT_BIT | self.RIGHT_RETINA_KEY_SET
        else:
            key_set_command = self.MANAGEMENT_BIT | self.LEFT_RETINA_KEY_SET

        # to ensure populations receive the correct packets, this needs to be
        # different based on which retina
        key_set_payload = (self._virtual_chip_x << 24 |
                           self._virtual_chip_y << 16)

        commands.append(MultiCastCommand(
            0, key_set_command, self.MANAGEMENT_MASK, key_set_payload,
            5, 1000))

        # make retina enabled (dependant on if its a left or right retina
        if position == self.RIGHT_RETINA:
            enable_command = self.MANAGEMENT_BIT | self.RIGHT_RETINA_ENABLE
        else:
            enable_command = self.MANAGEMENT_BIT | self.LEFT_RETINA_ENABLE
        commands.append(MultiCastCommand(
            0, enable_command, self.MANAGEMENT_MASK, 1, 5, 1000))

        # disable retina
        if position == self.RIGHT_RETINA:
            disable_command = self.MANAGEMENT_BIT | self.RIGHT_RETINA_DISABLE
        else:
            disable_command = self.MANAGEMENT_BIT | self.LEFT_RETINA_DISABLE

        commands.append(MultiCastCommand(
            -1, disable_command, self.MANAGEMENT_MASK, 0, 5, 1000))

        return commands

    def recieves_multicast_commands(self):
        return True

    def is_virtual_vertex(self):
        return True
