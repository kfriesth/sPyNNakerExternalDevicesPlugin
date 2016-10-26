from pacman.model.graphs.application.impl.application_spinnaker_link_vertex \
    import ApplicationSpiNNakerLinkVertex
from spinn_front_end_common.abstract_models.impl.\
    provides_key_to_atom_mapping_impl import \
    ProvidesKeyToAtomMappingImpl


class ExternalCochleaDevice(
        ApplicationSpiNNakerLinkVertex, ProvidesKeyToAtomMappingImpl):

    def __init__(
            self, n_neurons, spinnaker_link, label=None, board_address=None):
        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=n_neurons, spinnaker_link_id=spinnaker_link,
            label=label, max_atoms_per_core=n_neurons,
            board_address=board_address)
        ProvidesKeyToAtomMappingImpl.__init__(self)