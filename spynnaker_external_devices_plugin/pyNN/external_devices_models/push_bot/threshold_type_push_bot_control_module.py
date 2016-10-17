from spynnaker.pyNN.models.neural_properties.neural_parameter \
    import NeuronParameter
from data_specification.enums.data_type import DataType
from spynnaker.pyNN.models.neuron.threshold_types.abstract_threshold_type \
    import AbstractThresholdType
import math

class ThresholdTypePushBotControlModule(AbstractThresholdType):
    """ A threshold that is a static value
    """

    def __init__(
            self, n_neurons, uart_id, mapping, protocol_key_offset_mapping):
        AbstractThresholdType.__init__(self)
        self._n_neurons = n_neurons
        self._uart_id = uart_id
        self._ids = list()
        self._protocol_key_offset = list()

        # build a id flag set for the c code to deduce what functionality
        #  to execute per neuron
        for neuron_id in range(0, n_neurons):
            self._ids.append(mapping[neuron_id])
            self._protocol_key_offset.append(
                 protocol_key_offset_mapping[neuron_id])

    def get_n_threshold_parameters(self):
        return 3

    def get_threshold_parameters(self):
        return [
            NeuronParameter(self._ids, DataType.UINT32),
            NeuronParameter(self._uart_id, DataType.UINT32),
            NeuronParameter(self._protocol_key_offset, DataType.UINT32)
        ]

    def get_n_cpu_cycles_per_neuron(self):

        # Just a comparison, but 2 just in case!
        return 2
