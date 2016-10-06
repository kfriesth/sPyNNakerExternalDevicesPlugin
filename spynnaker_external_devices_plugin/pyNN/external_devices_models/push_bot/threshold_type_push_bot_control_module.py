from spynnaker.pyNN.utilities import utility_calls
from spynnaker.pyNN.models.neural_properties.neural_parameter \
    import NeuronParameter
from data_specification.enums.data_type import DataType
from spynnaker.pyNN.models.neuron.threshold_types.abstract_threshold_type \
    import AbstractThresholdType


class ThresholdTypePushBotControlModule(AbstractThresholdType):
    """ A threshold that is a static value
    """

    def __init__(self, n_neurons, keys):
        AbstractThresholdType.__init__(self)
        self._n_neurons = n_neurons
        self._keys = keys

    def get_n_threshold_parameters(self):
        return 1

    def get_threshold_parameters(self):
        return [
            NeuronParameter(self._keys, DataType.S1615)
        ]

    def get_n_cpu_cycles_per_neuron(self):

        # Just a comparison, but 2 just in case!
        return 2
