
# pynn imports
from pacman.model.graphs.application.impl.\
    application_spinnaker_link_vertex import \
    ApplicationSpiNNakerLinkVertex
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.push_bot_ethernet.push_bot_laser_device import \
    PushBotLaserDevice
from spynnaker_external_devices_plugin.pyNN.protocols.\
    munich_io_spinnaker_link_protocol import MunichIoSpiNNakerLinkProtocol


class PushBotSpiNNakerLinkLaserDevice(
        PushBotLaserDevice, ApplicationSpiNNakerLinkVertex):

    def __init__(
            self, spinnaker_link_id, uart_id=0, start_active_time=0,
            start_total_period=0, start_frequency=0, label=None, n_neurons=1,
            board_address=None):

        # as you are working with a spinnaker link, you use a separate
        # command sender which needs different keys for routing key alloc to
        # work correctly (edges from different verts cannot share keys
        # currently).
        protocol = MunichIoSpiNNakerLinkProtocol(
            mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)

        PushBotLaserDevice.__init__(
            self, uart_id, start_active_time,
            start_total_period, start_frequency,
            command_sender_protocol=protocol)

        ApplicationSpiNNakerLinkVertex.__init__(
            self, spinnaker_link_id=spinnaker_link_id, n_atoms=n_neurons,
            board_address=board_address, label=label)
