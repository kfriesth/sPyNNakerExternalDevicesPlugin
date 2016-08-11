from pacman.model.constraints.partitioner_constraints.\
    partitioner_maximum_size_constraint import \
    PartitionerMaximumSizeConstraint
from pacman.model.decorators.overrides import overrides
from pacman.model.graphs.application.impl.application_virtual_vertex import \
    ApplicationVirtualVertex


class ExternalCochleaDevice(ApplicationVirtualVertex):
    """
    cochlea device connected via spinnaker link
    """

    def __init__(
            self, n_neurons, spinnaker_link, label=None):
        ApplicationVirtualVertex.__init__(
            self, n_neurons, spinnaker_link, label,
            [PartitionerMaximumSizeConstraint(n_neurons)])

    @property
    @overrides(ApplicationVirtualVertex.model_name)
    def model_name(self):
        return "ExternalCochleaDevice:{}".format(self.label)
