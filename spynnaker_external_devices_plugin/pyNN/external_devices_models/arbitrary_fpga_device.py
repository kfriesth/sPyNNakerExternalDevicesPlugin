# pacman imports
from abc import ABCMeta
from six import add_metaclass

from pacman.model.graphs.application.impl.application_fpga_vertex \
    import ApplicationFPGAVertex
from spinn_front_end_common.abstract_models.impl.provides_key_to_atom_mapping_impl import \
    ProvidesKeyToAtomMappingImpl


@add_metaclass(ABCMeta)
class ArbitraryFPGADevice(
        ApplicationFPGAVertex, ProvidesKeyToAtomMappingImpl):

    def __init__(
            self, n_neurons, fpga_link_id, fpga_id, board_address=None,
            label=None):
        ApplicationFPGAVertex.__init__(
            self, n_neurons, fpga_id, fpga_link_id, board_address, label)
        ProvidesKeyToAtomMappingImpl.__init__(self)
