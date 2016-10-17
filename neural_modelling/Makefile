MODELS = robot_motor_control push_bot_spinnaker_link_control_module_n_model/random_folder/random_folder_2
BUILD_DIRS := $(addprefix src/, $(MODELS))

all: $(BUILD_DIRS)
	for d in $(BUILD_DIRS); do (cd $$d; "$(MAKE)") || exit $$?; done

clean: $(BUILD_DIRS)
	for d in $(BUILD_DIRS); do (cd $$d; "$(MAKE)" clean) || exit $$?; done
