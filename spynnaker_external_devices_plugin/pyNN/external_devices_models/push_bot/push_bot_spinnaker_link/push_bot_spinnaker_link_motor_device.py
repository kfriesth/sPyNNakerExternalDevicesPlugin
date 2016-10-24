
# external devices plugin imports
from pacman.model.graphs.application.impl.\
    application_spinnaker_link_vertex import \
    ApplicationSpiNNakerLinkVertex
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    push_bot.push_bot_ethernet.push_bot_motor_device import \
    PushBotMotorDevice


class PushBotSpiNNakerLinkMotorDevice(
        PushBotMotorDevice, ApplicationSpiNNakerLinkVertex):

    def __init__(
            self, spinnaker_link_id, motor_id=0, uart_id=0, label=None,
            n_neurons=1, board_address=None):

        PushBotMotorDevice.__init__(self, motor_id, uart_id)
        ApplicationSpiNNakerLinkVertex.__init__(
            self, spinnaker_link_id=spinnaker_link_id, n_atoms=n_neurons,
            board_address=board_address, label=label)
