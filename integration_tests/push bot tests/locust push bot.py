
import itertools
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy

import spynnaker.pyNN as sim
import spynnaker_external_devices_plugin.pyNN as ext

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def persistance_to_tc(timestep, persistance):
    return -timestep / math.log(persistance)

def get_neuron_index(population_size, x, y):
    return x + (y * population_size)

def get_distance_squared(xi, yi, xj, yj):
    return ((xi - xj) ** 2 + (yi - yj) ** 2)

def get_centre_to_one_connection_list(pre_size, centre_size, weight, delay):
    # Connect all centre pixels of pre-synaptic population to single post synaptic neuron
    border_size = (pre_size - centre_size) / 2
    return [(get_neuron_index(pre_size, xi, yi), 0, weight, delay)
            for xi, yi in itertools.product(range(border_size, pre_size - border_size), repeat=2)]

def get_i_to_s_connection_list(pop_size, centre_size, weight_delay_dict):
    # Loop through post-synaptic central pixels
    border_size = (pop_size - centre_size) / 2
    connections = []
    for xj, yj in itertools.product(range(border_size, pop_size - border_size), repeat=2):
        # Loop through all pre-synaptic pixels between 1 and 2 pixels away from these
        for xi, yi in itertools.ifilter(lambda (xi, yi): 0 < get_distance_squared(xi, yi, xj, yj) <= 4, itertools.product(range(pop_size), repeat=2)):
            # Get weight delay corresponding to this pixels distance
            weight_delay = weight_delay_dict[get_distance_squared(xi, yi, xj, yj)]

            # Add connection
            connections.append((get_neuron_index(pop_size, xi, yi), get_neuron_index(pop_size, xj, yj), weight_delay[0], weight_delay[1]))
    return connections

def get_retina_connection_list(pop_size, coordinate_bits, weight, delay):
    connections = []
    polarity = 1 << (coordinate_bits * 2)
    for x, y in itertools.product(range(pop_size), repeat=2):
        i = get_neuron_index(pop_size, x, y)

        # Connect both polarities
        connections.append((i, i, weight, delay))
        #connections.append((i | polarity, i, weight, delay))
    return connections

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
timestep = 1.0

input_size = 32
centre_size = 20

timesteps_per_frame = 33

persistance_e = 0.1
persistance_i = 0.8
persistance_s = 0.4
persistance_f = 0.1
persistance_lgmd = 0.4

i_s_weight_scale = 0.2 * 2.0 * 0.04
i_s_weight_delay_dict = {
    1: (-0.4 * i_s_weight_scale, 3),
    2: (-0.32 * i_s_weight_scale, 3),
    4: (-0.2 * i_s_weight_scale, 4)
}

# Convergent connection weights need to be scaled as out
convergent_strength = 0.04 * (16.0 ** 2 / float(centre_size) ** 2)
print("Convergent strength %f" % convergent_strength)

# Convert persistences to taus
scale = 10.0
tau_s = persistance_to_tc(timestep, persistance_s) * scale
tau_i = persistance_to_tc(timestep, persistance_i) * scale
tau_e = persistance_to_tc(timestep, persistance_e) * scale
tau_lgmd = persistance_to_tc(timestep, persistance_lgmd) * scale
tau_f = persistance_to_tc(timestep, persistance_f) * scale

print("Tau s:%f, Tau i:%f, Tau e:%f, Tau lgmd:%f, Tau_f:%f" % (tau_s, tau_i, tau_e, tau_lgmd, tau_f))

p_max_time = 10000

sim.setup(timestep=1.0, min_delay=1.0, max_delay=15.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 100)

# -----------------------------------------------------------------------------
# Populations
# -----------------------------------------------------------------------------
# Create virtual retina population
# **NOTE** many params actually ignored
population_r = sim.Population(None, ext.PushBotRetinaDevice, { "connected_to_real_chip_x": 1, "connected_to_real_chip_y": 0, "connected_to_real_chip_link_id": 0,
    "virtual_chip_x": 6, "virtual_chip_y": 0, "polarity": ext.PushBotRetinaDevice.UP_POLARITY})

# Create dummy proxy population
# **TODO** not necessary, just just useful for recording
population_p = sim.Population(input_size ** 2, sim.IF_curr_exp, {})

# Connect it with magic up and down merging population
sim.Projection(population_r, population_p, sim.FromListConnector(get_retina_connection_list(input_size, 5, 16.0, 1)))

population_s = sim.Population(input_size ** 2,
                              sim.IF_curr_exp,{"v_rest": 0.0, "i_offset": 0.0, "v_thresh": 0.5, "tau_m": tau_s, "v_reset": 0.0,
                                               "tau_syn_I": tau_i, "tau_syn_E": tau_e, "tau_refrac": 1.0, "cm": 1.0})
population_lgmd = sim.Population(1,
                                 sim.IF_curr_exp,{"v_rest": 0.0, "i_offset": 0.0, "v_thresh": 0.25, "tau_m": tau_lgmd, "v_reset": 0.0,
                                                "tau_syn_I": tau_f, "tau_syn_E": 4.0, "tau_refrac": 1.0, "cm": 1.0})

population_motor = sim.Population(1, sim.IZK_curr_exp,{})
6
# -----------------------------------------------------------------------------
# Projections
# -----------------------------------------------------------------------------
# P->F->LGMD
sim.Projection(population_p, population_lgmd,
               sim.FromListConnector(get_centre_to_one_connection_list(input_size, centre_size, -convergent_strength * 5.0 * 0.2, 3.0)), target="inhibitory")
# S->LGMD
sim.Projection(population_s, population_lgmd,
               sim.FromListConnector(get_centre_to_one_connection_list(input_size, centre_size, convergent_strength * 2.0 * 4.0, 1.0)), target="excitatory")
# P->E->S
sim.Projection(population_p, population_s,
               sim.OneToOneConnector(weights=0.6 * 2.0, delays=2.0), target="excitatory")

# P->I->S
sim.Projection(population_p, population_s,
               sim.FromListConnector(get_i_to_s_connection_list(input_size, centre_size, i_s_weight_delay_dict)), target="inhibitory")

sim.Projection(population_lgmd, population_motor, sim.OneToOneConnector(), target="excitatory")
# -----------------------------------------------------------------------------
# Recording
# -----------------------------------------------------------------------------
#population_s.record_v()
#population_s.record()
population_p.record()
population_lgmd.record_v()

# -----------------------------------------------------------------------------
# Simulation
# -----------------------------------------------------------------------------
sim.run(p_max_time)

# -----------------------------------------------------------------------------
# Reading
# -----------------------------------------------------------------------------
v_lgmd = population_lgmd.get_v(compatible_output=True)
p_p = population_p.getSpikes(compatible_output=True)

sim.end()

# -----------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------
fig = plt.figure()

p_axis = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
p_axis.set_title("Retina spikes")

lgmd_axis = plt.subplot2grid((3, 2), (2, 0), colspan=4)
lgmd_axis.set_title("LGMD membrane voltage")
lgmd_axis.set_ylim((0.0, 0.25))
lgmd_axis.plot(v_lgmd[:,1], v_lgmd[:,2], label="LGMD")

# Show empty image in p
input_image_data = numpy.zeros((input_size, input_size))
p_image = p_axis.imshow(input_image_data, interpolation="nearest", cmap="jet", vmin=0.0, vmax=33.0)

# Animate voltages
def update_voltages(frame):
    global input_image_data
    global p_image
    global input_size
    global p_p

    # Get mask of retina spikes that occur during frame
    start_timestep = frame * timesteps_per_frame
    frame_mask = numpy.logical_and((p_p[:,1] >= start_timestep), (p_p[:,1] < (start_timestep + timesteps_per_frame)))

    # Use these to get voltages
    #frame_v_s = v_s[frame_mask][:,2]
    frame_p_p = p_p[frame_mask][:,0]

    # Decay image data
    input_image_data *= 0.9

    # Loop through all timesteps that occur within frame
    for k in frame_p_p:
        x = int(k) / 32
        y = int(k) % 32

        # Set frame
        input_image_data[x, y] = 1.0
    p_image.set_array(input_image_data)

    return [p_image]

# Play animation
ani = animation.FuncAnimation(fig, update_voltages, range(p_max_time / timesteps_per_frame), interval=timesteps_per_frame, blit=True, repeat=True)

# Show plots
plt.show()