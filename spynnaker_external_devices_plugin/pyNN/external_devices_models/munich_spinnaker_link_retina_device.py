# front end common imports
from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_fixed_key_and_mask_constraint \
    import KeyAllocatorFixedKeyAndMaskConstraint
from pacman.model.graphs.application.impl.application_spinnaker_link_vertex \
    import ApplicationSpiNNakerLinkVertex
from pacman.model.routing_info.base_key_and_mask import BaseKeyAndMask
from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints
from spinn_front_end_common.abstract_models.impl.\
    send_me_multicast_commands_vertex import SendMeMulticastCommandsVertex
from spinn_front_end_common.utility_models.\
    commands.multi_cast_command_with_payload import \
    MultiCastCommandWithPayload
from spynnaker.pyNN import exceptions

# robot with 7 7 1


def get_x_from_robot_retina(key):
    return (key >> 7) & 0x7f


def get_y_from_robot_retina(key):
    return key & 0x7f


def get_spike_value_from_robot_retina(key):
    return (key >> 14) & 0x1


class MunichRetinaDevice(
        ApplicationSpiNNakerLinkVertex, SendMeMulticastCommandsVertex,
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

    def __init__(
            self, retina_key, spinnaker_link_id, position,
            label=None, n_neurons=None, polarity=None, board_address=None):

        if polarity is None:
            polarity = MunichRetinaDevice.MERGED_POLARITY

        self._fixed_key = (retina_key & 0xFFFF) << 16
        self._fixed_mask = 0xFFFF8000
        if polarity == MunichRetinaDevice.UP_POLARITY:
            self._fixed_key |= 0x4000

        if polarity == MunichRetinaDevice.MERGED_POLARITY:

            # There are 128 x 128 retina "pixels" x 2 polarities
            fixed_n_neurons = 128 * 128 * 2
        else:

            # There are 128 x 128 retina "pixels"
            fixed_n_neurons = 128 * 128
            self._fixed_mask = 0xFFFFC000

        self._polarity = polarity
        self._position = position

        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=fixed_n_neurons, spinnaker_link_id=spinnaker_link_id,
            max_atoms_per_core=fixed_n_neurons, label=label,
            board_address=board_address)
        SendMeMulticastCommandsVertex.__init__(
            self, start_resume_commands=self._start_pause_commands(),
            pause_stop_commands=self._pause_stop_commands(),
            timed_commands=self._get_timed_commands())
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

        if (self._position != self.RIGHT_RETINA and
           self._position != self.LEFT_RETINA):
            raise exceptions.SpynnakerException(
                "The external Retina does not recognise this _position")

        if n_neurons != fixed_n_neurons and n_neurons is not None:
            print "Warning, the retina will have {} neurons".format(
                fixed_n_neurons)

    def get_outgoing_partition_constraints(self, partition):
        return [KeyAllocatorFixedKeyAndMaskConstraint(
            [BaseKeyAndMask(self._fixed_key, self._fixed_mask)])]

    def _start_pause_commands(self):
        commands = list()
        # change the retina key it transmits with
        # (based off if its right or left)
        if self._position == self.RIGHT_RETINA:
            key_set_command = self.MANAGEMENT_BIT | self.RIGHT_RETINA_KEY_SET
        else:
            key_set_command = self.MANAGEMENT_BIT | self.LEFT_RETINA_KEY_SET

        # to ensure populations receive the correct packets, this needs to be
        # different based on which retina
        key_set_payload = (self._virtual_chip_x << 24 |
                           self._virtual_chip_y << 16)

        commands.append(MultiCastCommandWithPayload(
            0, key_set_command, key_set_payload, 5, 1000))

        # make retina enabled (dependent on if its a left or right retina
        if self._position == self.RIGHT_RETINA:
            enable_command = self.MANAGEMENT_BIT | self.RIGHT_RETINA_ENABLE
        else:
            enable_command = self.MANAGEMENT_BIT | self.LEFT_RETINA_ENABLE
        commands.append(
            MultiCastCommandWithPayload(0, enable_command, 1, 5, 1000))

    def _pause_stop_commands(self):
        commands = list()
         # disable retina
        if self._position == self.RIGHT_RETINA:
            disable_command = self.MANAGEMENT_BIT | self.RIGHT_RETINA_DISABLE
        else:
            disable_command = self.MANAGEMENT_BIT | self.LEFT_RETINA_DISABLE

        commands.append(
            MultiCastCommandWithPayload(-1, disable_command, 0, 5, 1000))

    @staticmethod
    def _get_timed_commands():
        return []