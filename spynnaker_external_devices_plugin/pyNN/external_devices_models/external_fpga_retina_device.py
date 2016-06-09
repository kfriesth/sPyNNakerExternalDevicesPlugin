import logging

from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spynnaker.pyNN.models.abstract_models\
    .abstract_send_me_multicast_commands_vertex \
    import AbstractSendMeMulticastCommandsVertex
from spynnaker.pyNN import exceptions
from spynnaker.pyNN.utilities.multi_cast_command import MultiCastCommand
from pacman.model.abstract_classes.abstract_virtual_vertex \
    import AbstractVirtualVertex
from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_fixed_key_and_mask_constraint \
    import KeyAllocatorFixedKeyAndMaskConstraint
from pacman.model.routing_info.base_key_and_mask import BaseKeyAndMask

logger = logging.getLogger(__name__)


def get_y_from_fpga_retina(key, mode):
    if mode == 128:
        return key & 0x7f
    elif mode == 64:
        return key & 0x3f
    elif mode == 32:
        return key & 0x1f
    elif mode == 16:
        return key & 0xf
    else:
        return None


def get_x_from_fpga_retina(key, mode):
    if mode == 128:
        return (key >> 7) & 0x7f
    elif mode == 64:
        return (key >> 6) & 0x3f
    elif mode == 32:
        return (key >> 5) & 0x1f
    elif mode == 16:
        return (key >> 4) & 0xf
    else:
        return None


def get_spike_value_from_fpga_retina(key, mode):
    if mode == 128:
        return (key >> 14) & 0x1
    elif mode == 64:
        return (key >> 14) & 0x1
    elif mode == 32:
        return (key >> 14) & 0x1
    elif mode == 16:
        return (key >> 14) & 0x1
    else:
        return None


class ExternalFPGARetinaDevice(
        AbstractVirtualVertex, AbstractSendMeMulticastCommandsVertex,
        AbstractProvidesOutgoingPartitionConstraints):

    MODE_128 = "128"
    MODE_64 = "64"
    MODE_32 = "32"
    MODE_16 = "16"
    UP_POLARITY = "UP"
    DOWN_POLARITY = "DOWN"
    MERGED_POLARITY = "MERGED"
    DEFAULT_FIXED_MASK = 0xFFFF8000

    """
        :param mode: The retina "mode"
        :param retina_key: The value of the top 16-bits of the key
        :param spinnaker_link_id: The spinnaker link to which the retina is\
                connected
        :param polarity: The "polarity" of the retina data
        :param label: The label for the population
        :param n_neurons: The number of neurons in the population
    """
    population_parameters = {
        'spinnaker_link', 'polarity', 'retina_key', 'mode'}

    model_name = "external FPGA retina device"

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

    def __init__(self, bag_of_neurons, label):
        """
        entrance for a fpga retina device
        :param bag_of_neurons: the atoms covered by this vertex
        :param label: the bale of this vertex
        :return:
        """

        self._atoms = bag_of_neurons

        # assume polarity is same for all atoms (as pop scoped)
        polarity = bag_of_neurons[0].get_population_parameter('polarity')

        # assume retina key is same for all atoms (as pop scoped)
        fixed_key = bag_of_neurons[0].get_population_parameter('retina_key')
        fixed_key = (fixed_key& 0xFFFF) << 16

        # update fixed key based off polarity
        if polarity == ExternalFPGARetinaDevice.UP_POLARITY:
            fixed_key |= 0x4000

        # update all atoms with new fixed_key
        for atom in bag_of_neurons:
            atom.set_population_parameter('retina_key', fixed_key)

        # assume mode is same for all atoms (as pop scoped)
        mode = bag_of_neurons[0].get_population_parameter('mode')

        # assume spinnaker link is same for all atoms (as pop scoped)
        spinnaker_link_id =\
            bag_of_neurons[0].get_population_parameter('spinnaker_link_id')

        # get default fixed mask
        self._fixed_mask = ExternalFPGARetinaDevice.DEFAULT_FIXED_MASK

        if mode == ExternalFPGARetinaDevice.MODE_128:
            if (polarity == ExternalFPGARetinaDevice.UP_POLARITY or
                    polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                fixed_n_neurons = 128 * 128
                self._fixed_mask = 0xFFFFC000
            else:
                fixed_n_neurons = 128 * 128 * 2
        elif mode == ExternalFPGARetinaDevice.MODE_64:
            if (polarity == ExternalFPGARetinaDevice.UP_POLARITY or
                    polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                fixed_n_neurons = 64 * 64
                self._fixed_mask = 0xFFFFF000
            else:
                fixed_n_neurons = 64 * 64 * 2
        elif mode == ExternalFPGARetinaDevice.MODE_32:
            if (polarity == ExternalFPGARetinaDevice.UP_POLARITY or
                    polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                fixed_n_neurons = 32 * 32
                self._fixed_mask = 0xFFFFFC00
            else:
                fixed_n_neurons = 32 * 32 * 2
        elif mode == ExternalFPGARetinaDevice.MODE_16:
            if (polarity == ExternalFPGARetinaDevice.UP_POLARITY or
                    polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                fixed_n_neurons = 16 * 16
                self._fixed_mask = 0xFFFFFF00
            else:
                fixed_n_neurons = 16 * 16 * 2
        else:
            raise exceptions.SpynnakerException(
                "the FPGA retina does not recognise this mode")

        if fixed_n_neurons != len(bag_of_neurons):
            logger.warn("The specified number of neurons for the FPGA retina"
                        " device has been ignored {} will be used instead"
                        .format(fixed_n_neurons))
        AbstractVirtualVertex.__init__(
            self, fixed_n_neurons, spinnaker_link_id,
            max_atoms_per_core=fixed_n_neurons, label=label)
        AbstractSendMeMulticastCommandsVertex.__init__(self, commands=[
            MultiCastCommand(0, 0x0000FFFF, 0xFFFF0000, 1, 5, 100),
            MultiCastCommand(-1, 0x0000FFFE, 0xFFFF0000, 0, 5, 100)])
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

    def get_outgoing_partition_constraints(self, partition, graph_mapper):

        # assume retina key is same for all atoms (as pop scoped)
        fixed_key = self._n_atoms[0].get_population_parameter('retina_key')

        return [KeyAllocatorFixedKeyAndMaskConstraint(
            [BaseKeyAndMask(fixed_key, self._fixed_mask)])]

    def is_virtual_vertex(self):
        return True

    def recieves_multicast_commands(self):
        return True
