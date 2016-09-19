from pacman.model.decorators.overrides import overrides
from pacman.model.graphs.machine.impl.machine_vertex import MachineVertex


class ExternalDevicesMachineVertex(MachineVertex):
    """
    impl of the machine vertex so that it contains resources and can be used
    by vertices which do not need their own bespoke machine verts.
    """

    def __init__(self, resources, label, constraints):
        self._resources = resources
        MachineVertex.__init__(self, label, constraints)

    @overrides(MachineVertex.resources_required)
    def resources_required(self):
        return self._resources