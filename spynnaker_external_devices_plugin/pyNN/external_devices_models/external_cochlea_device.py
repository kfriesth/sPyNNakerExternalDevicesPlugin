from pacman.model.abstract_classes.abstract_spinnaker_link_vertex import \
    AbstractSpiNNakerLinkVertex


class ExternalCochleaDevice(AbstractSpiNNakerLinkVertex):

    def __init__(
            self, n_neurons, spinnaker_link, machine_time_step,
            timescale_factor, label=None, board_address=None):
        AbstractSpiNNakerLinkVertex.__init__(
            self, n_atoms=n_neurons, spinnaker_link_id=spinnaker_link,
            label=label, max_atoms_per_core=n_neurons,
            board_address=board_address)

    @property
    def model_name(self):
        return "ExternalCochleaDevice:{}".format(self.label)

    def is_virtual_vertex(self):
        return True
