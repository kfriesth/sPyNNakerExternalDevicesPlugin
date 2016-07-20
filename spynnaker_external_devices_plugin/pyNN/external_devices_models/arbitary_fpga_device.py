# pacman imports

# external devices imports
from pacman.model.abstract_classes.abstract_fpga_vertex\
    import AbstractFPGAVertex

# general imports
from abc import ABCMeta
from six import add_metaclass


@add_metaclass(ABCMeta)
class ArbitaryFPGADevice(AbstractFPGAVertex):

    def __init__(
            self, n_neurons, fpga_link_id, fpga_id, machine_time_step,
            timescale_factor, board_address=None, label=None):
        AbstractFPGAVertex.__init__(
            self, n_neurons, fpga_link_id, fpga_id, machine_time_step,
            timescale_factor, board_address, label)

    @property
    def model_name(self):
        return "ArbitarySATADevice:{}".format(self.label)