import spynnaker.pyNN as p
import spynnaker_external_devices_plugin.pyNN as q

n_neurons_per_command = 20
n_neurons_per_synapse_type = 10
n_commands = 4
n_neurons = n_neurons_per_command * n_commands

# Setup
p.setup(timestep=1.0)

push_bot_control_module = p.Population(
    2,
    q.PushBotSpinnakerLinkControlModuleNModel,
    {
        'spinnaker_link_id': 0, 'speaker_start_frequency': 0,
        'motor_0_leaky_velocity_neuron_id': 0,
        'motor_1_leaky_velocity_neuron_id': 1,
        'tau_syn_E': 100,
        'uart_id': 0
    })

timer_ticks_between_test = 1000
spike_times = list()

# handle neurons
for command in range(0, n_commands):
    # inhib
    for neuron_id in range(0, n_neurons_per_synapse_type):
        data = list()
        start_time = \
            command * (n_neurons_per_command * timer_ticks_between_test)
        for time in range(0 + neuron_id, n_neurons_per_synapse_type):
            data.append(start_time + (time * timer_ticks_between_test))
        spike_times.append(data)
    # excit
    for neuron_id in range(0, n_neurons_per_synapse_type):
        data = list()
        start_time = \
            (command * (n_neurons_per_command * timer_ticks_between_test)) + \
            (n_neurons_per_synapse_type * timer_ticks_between_test)
        for time in range(0 + neuron_id, n_neurons_per_synapse_type):
            data.append(start_time + (time * timer_ticks_between_test))
        spike_times.append(data)


ssa = p.Population(n_neurons, p.SpikeSourceArray, {'spike_times': spike_times})

# 4 neurons per
connection_list_inhib = list()
connection_list_excit = list()

for motor_behaviour in range(0, 2):
    for neuron in range(0, n_neurons_per_command):
        if neuron > n_neurons_per_synapse_type - 1:
            connection_list_excit.append(
                [neuron + (motor_behaviour * n_neurons_per_command),
                 motor_behaviour, 10, 1])
        else:
            connection_list_inhib.append(
                [neuron + (motor_behaviour * n_neurons_per_command),
                 motor_behaviour, 10, 1])

p.Projection(ssa, push_bot_control_module,
             p.FromListConnector(connection_list_inhib), target="inhibitory")
p.Projection(ssa, push_bot_control_module,
             p.FromListConnector(connection_list_excit), target="excitatory")

# Run infinite simulation (non-blocking)
p.run(40000)

# End simulation
p.end()