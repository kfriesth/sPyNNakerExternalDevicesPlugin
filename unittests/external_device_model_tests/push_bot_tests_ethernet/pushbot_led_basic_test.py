import spynnaker.pyNN as p
import spynnaker_external_devices_plugin.pyNN as q
import pylab

n_neurons_per_command = 20
n_neurons_per_synapse_type = 10
n_commands = 4
n_neurons = n_neurons_per_command * n_commands

# Setup
p.setup(timestep=1.0)

retina_pop, push_bot_control_module, push_bot_connection = \
    q.push_bot_ethernet_connection(
        spinnaker_control_packet_port=11111,
        spinnaker_injection_packet_port=22222,
        speaker_start_frequency=0,
        leds_total_period_neuron_id=0,
        front_led_active_time_neuron_id=1,
        back_led_active_time_neuron_id=2,
        led_frequency_neuron_id=3,
        control_n_neurons=3,
        push_bot_ip_address="10.162.177.57")

timer_ticks_between_test = 10
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

push_bot_control_module.record_v()

# Run infinite simulation (non-blocking)
p.run(20000)


v = push_bot_control_module.get_v()

if v is not None:
    ticks = len(v) / 1
    pylab.figure()
    pylab.xlabel('Time/ms')
    pylab.ylabel('v')
    pylab.title('v')
    for pos in range(0, 1, 20):
        v_for_neuron = v[pos * ticks: (pos + 1) * ticks]
        pylab.plot([i[2] for i in v_for_neuron])
    pylab.show()

# End simulation
p.end()
