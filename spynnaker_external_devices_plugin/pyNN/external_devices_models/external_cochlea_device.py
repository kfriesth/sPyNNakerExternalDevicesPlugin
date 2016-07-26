from pacman.model.graph.application.simple_virtual_application_vertex \
    import SimpleVirtualApplicationVertex


class ExternalCochleaDevice(SimpleVirtualApplicationVertex):

    def __init__(
            self, n_neurons, spinnaker_link, machine_time_step,
            timescale_factor, label=None):
        SimpleVirtualApplicationVertex.__init__(
            self, n_neurons, spinnaker_link, label=label,
            max_atoms_per_core=n_neurons)

    @property
    def model_name(self):
        return "ExternalCochleaDevice:{}".format(self.label)

    def is_virtual_vertex(self):
        return True
