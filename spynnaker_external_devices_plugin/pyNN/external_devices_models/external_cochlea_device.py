from pacman.model.abstract_classes.abstract_virtual_vertex \
    import AbstractVirtualVertex


class ExternalCochleaDevice(AbstractVirtualVertex):

    population_parameters = {
        'machine_time_step', 'time_scale_factor', 'spinnaker_link'}

    model_name = "ExternalCochleaDevice"

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

        # can assume spinnaker link is consistent between atoms, as its a
        # population parameter
        spinnaker_link = \
            bag_of_neurons[0].get_population_parameter('spinnaker_link')

        AbstractVirtualVertex.__init__(
            self, len(bag_of_neurons), spinnaker_link, label=label,
            max_atoms_per_core=len(bag_of_neurons))

    def is_virtual_vertex(self):
        return True
