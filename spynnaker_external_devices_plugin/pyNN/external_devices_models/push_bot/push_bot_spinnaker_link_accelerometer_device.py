
# pynn imports
from pacman.model.constraints.key_allocator_constraints.\
    key_allocator_fixed_key_and_mask_constraint import \
    KeyAllocatorFixedKeyAndMaskConstraint
from pacman.model.decorators.overrides import overrides
from pacman.model.graphs.application.impl.application_spinnaker_link_vertex \
    import ApplicationSpiNNakerLinkVertex
from pacman.model.routing_info.base_key_and_mask import BaseKeyAndMask
from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_partition_constraints import \
    AbstractProvidesOutgoingPartitionConstraints

from spinn_front_end_common.abstract_models.impl.\
    send_me_multicast_commands_vertex import SendMeMulticastCommandsVertex

from spynnaker_external_devices_plugin.pyNN.protocols.\
    munich_io_spinnaker_link_protocol import MunichIoSpiNNakerLinkProtocol

UART_ID = 0
SENSOR_ACCELEROMETER_ID = 8


class PushBotSpiNNakerLinkAccelerometerDevice(
        ApplicationSpiNNakerLinkVertex, SendMeMulticastCommandsVertex,
        AbstractProvidesOutgoingPartitionConstraints):

    def __init__(
            self, spinnaker_link_id, sensor_in_millisecond=100, motor_id=0,
            uart_id=0, label=None, n_neurons=1, board_address=None):

        # munich protocol
        self._protocol = MunichIoSpiNNakerLinkProtocol(
            mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)

        self._motor_id = motor_id
        self._uart_id = uart_id
        self._sensor_in_millisecond = sensor_in_millisecond

        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=n_neurons, spinnaker_link_id=spinnaker_link_id,
            max_atoms_per_core=n_neurons, label=label,
            board_address=board_address)
        SendMeMulticastCommandsVertex.__init__(
            self, start_resume_commands=self._get_start_resume_commands(),
            pause_stop_commands=self._get_pause_stop_commands(),
            timed_commands=self._get_timed_commands())
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)

    def _get_start_resume_commands(self):
        commands = list()

        # add mode command if not done already
        if not self._protocol.has_set_off_configuration_command():
            commands.append(self._protocol.get_set_mode_command())

        # device specific commands
        commands.append(self._protocol.poll_individual_sensor_continuously(
            sensor_id=SENSOR_ACCELEROMETER_ID, time=0,
            time_in_ms=self._sensor_in_millisecond))
        return commands

    def _get_pause_stop_commands(self):
        commands = list()
        commands.append(
            self._protocol.turn_off_sensor_reporting(
                sensor_id=SENSOR_ACCELEROMETER_ID, time=-1))
        return commands

    @staticmethod
    def _get_timed_commands():
        return []

    @property
    def uart_id(self):
        return self._uart_id

    @overrides(AbstractProvidesOutgoingPartitionConstraints.
               get_outgoing_partition_constraints)
    def get_outgoing_partition_constraints(self, partition):
        constraints = list()
        constraints.append(
            KeyAllocatorFixedKeyAndMaskConstraint(
                [BaseKeyAndMask(
                    self._protocol.sensor_transmission_key(
                        sensor_id=SENSOR_ACCELEROMETER_ID,
                        uart_id=self._uart_id),
                    0xFFFFFFF8)]))
        return constraints

    @property
    def model_name(self):
        return "push_bot_accelerometer_device"
