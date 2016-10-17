APP = push_bot_spinnaker_link_control_module_n_model
BUILD_DIR = build/

NEURON_MODEL = $(SOURCE_DIR)/neuron/models/neuron_model_lif_impl.c
NEURON_MODEL_H = $(SOURCE_DIR)/neuron/models/neuron_model_lif_impl.h
INPUT_TYPE_H = $(SOURCE_DIR)/neuron/input_types/input_type_current.h
THRESHOLD_TYPE_H = $(EXTRA_SRC_DIR)/push_bot_spinnaker_link_control_module_n_model/random_folder/random_folder_2/threshold_type_push_bot_control_module.h
SYNAPSE_TYPE_H = $(SOURCE_DIR)/neuron/synapse_types/synapse_types_exponential_impl.h
SYNAPSE_DYNAMICS = $(SOURCE_DIR)/neuron/plasticity/synapse_dynamics_static_impl.c

include $(NEURAL_MODELLING_DIRS)/src/neuron/builds/Makefile.common
