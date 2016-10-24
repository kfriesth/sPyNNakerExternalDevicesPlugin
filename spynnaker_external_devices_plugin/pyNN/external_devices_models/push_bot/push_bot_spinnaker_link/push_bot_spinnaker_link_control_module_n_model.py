from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link.push_bot_spinnaker_link_led_device import \
    PushBotSpiNNakerLinkLEDDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link.push_bot_spinnaker_link_speaker_device import \
    PushBotSpiNNakerLinkSpeakerDevice
from spinn_front_end_common.abstract_models.impl.\
    vertex_with_dependent_vertices import \
    VertexWithEdgeToDependentVertices
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link.push_bot_spinnaker_link_motor_device import \
    PushBotSpiNNakerLinkMotorDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    push_bot.abstract_push_bot_control_module_model import \
    AbstractPushBotControlModuleModel
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.\
    push_bot_spinnaker_link.push_bot_spinnaker_link_laser_device import \
    PushBotSpiNNakerLinkLaserDevice

import logging

logger = logging.getLogger(__name__)


class PushBotSpinnakerLinkControlModuleNModel(
        AbstractPushBotControlModuleModel, VertexWithEdgeToDependentVertices):
    """ Leaky integrate and fire neuron with an exponentially decaying \
        current input
    """

    def __init__(
            self, n_neurons, spinnaker_link_id, spikes_per_second=None,
            ring_buffer_sigma=None, label=None,
            incoming_spike_buffer_size=None, constraints=None,

            # default params for the neuron model type
            tau_m=
            AbstractPushBotControlModuleModel.default_parameters['tau_m'],
            cm=AbstractPushBotControlModuleModel.default_parameters['cm'],
            v_rest=
            AbstractPushBotControlModuleModel.default_parameters['v_rest'],
            v_reset=
            AbstractPushBotControlModuleModel.default_parameters['v_reset'],
            tau_syn_E=
            AbstractPushBotControlModuleModel.default_parameters['tau_syn_E'],
            tau_syn_I=
            AbstractPushBotControlModuleModel.default_parameters['tau_syn_I'],
            tau_refrac=
            AbstractPushBotControlModuleModel.default_parameters['tau_refrac'],
            i_offset=
            AbstractPushBotControlModuleModel.default_parameters['i_offset'],
            v_init=None,
            # global for all devices that this control module works with
            board_address=None, uart_id=0,
            # the laser bespoke setup params
            laser_start_active_time=0, laser_start_total_period=0,
            laser_start_frequency=0,
            # the front led bespoke setup params
            front_led_start_active_time=0,
            front_led_total_period=0, front_led_start_frequency=0,
            # the back led bespoke setup params
            back_led_start_active_time=0,
            back_led_total_period=0, back_led_start_frequency=0,
            # the speaker bespoke setup params
            speaker_start_active_time=0, speaker_start_total_period=0,
            speaker_start_frequency=None, speaker_melody_value=None,
            # neuron_ids for devices
            motor_0_permanent_velocity_neuron_id=None,
            motor_0_leaky_velocity_neuron_id=None,
            motor_1_permanent_velocity_neuron_id=None,
            motor_1_leaky_velocity_neuron_id=None,
            laser_total_period_neuron_id=None,
            speaker_total_period_neuron_id=None,
            leds_total_period_neuron_id=None,
            laser_active_time_neuron_id=None,
            speaker_active_time_neuron_id=None,
            front_led_active_time_neuron_id=None,
            back_led_active_time_neuron_id=None,
            speaker_tone_frequency_neuron_id=None,
            speaker_melody_neuron_id=None,
            laser_frequency_neuron_id=None,
            led_frequency_neuron_id = None
    ):

        laser_device = PushBotSpiNNakerLinkLaserDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, start_active_time=laser_start_active_time,
            start_total_period=laser_start_total_period,
            start_frequency=laser_start_frequency, label="the push bot laser")

        led_device_front = PushBotSpiNNakerLinkLEDDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, start_active_time=front_led_start_active_time,
            front_led=True, start_total_period=front_led_total_period,
            start_frequency=front_led_start_frequency,
            label="the push bot front led")

        led_device_back = PushBotSpiNNakerLinkLEDDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, start_active_time=back_led_start_active_time,
            front_led=False, start_total_period=back_led_total_period,
            start_frequency=back_led_start_frequency,
            label="The push bot back led")

        motor_0 = PushBotSpiNNakerLinkMotorDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, motor_id=0, label="The push bot first motor")

        motor_1 = PushBotSpiNNakerLinkMotorDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            uart_id=uart_id, motor_id=1, label="The push bot second motor")

        speaker = PushBotSpiNNakerLinkSpeakerDevice(
            spinnaker_link_id=spinnaker_link_id, board_address=board_address,
            start_active_time=speaker_start_active_time,
            start_total_period=speaker_start_total_period,
            start_frequency=speaker_start_frequency,
            melody_value=speaker_melody_value, label="The push bot speaker")

        VertexWithEdgeToDependentVertices.__init__(
            self,
            {laser_device: [self.LASER_TOTAL_PERIOD_PARTITION_ID,
                            self.LASER_ACTIVE_TIME_PARTITION_ID,
                            self.LASER_FREQUENCY_PARTITION_ID],
             led_device_front: [self.LED_FRONT_TOTAL_PERIOD_PARTITION_ID,
                                self.LED_FRONT_ACTIVE_TIME_PARTITION_ID,
                                self.LED_FRONT_FREQUENCY_PARTITION_ID],
             led_device_back: [self.LED_BACK_ACTIVE_TIME_PARTITION_ID],
             motor_0: [self.MOTOR_0_PERMANENT_PARTITION_ID,
                       self.MOTOR_0_LEAKY_PARTITION_ID],
             motor_1: [self.MOTOR_1_PERMANENT_PARTITION_ID,
                       self.MOTOR_1_LEAKY_PARTITION_ID],
             speaker: [self.SPEAKER_TOTAL_PERIOD_PARTITION_ID,
                       self.SPEAKER_ACTIVE_TIME_PARTITION_ID,
                       self.SPEAKER_TONE_FREQUENCY_PARTITION_ID,
                       self.SPEAKER_MELODY_PARTITION_ID]})

        AbstractPushBotControlModuleModel.__init__(
            self, n_neurons=n_neurons, laser_vertex=laser_device,
            speaker_vertex=speaker, front_led=led_device_front,
            back_led=led_device_back, motor_0=motor_0, motor_1=motor_1,
            spikes_per_second=spikes_per_second, label=label,
            ring_buffer_sigma=ring_buffer_sigma,
            incoming_spike_buffer_size=incoming_spike_buffer_size,
            constraints=constraints,
            tau_m=tau_m, cm=cm, v_rest=v_rest, v_reset=v_reset,
            tau_syn_E=tau_syn_E, tau_syn_I=tau_syn_I,
            tau_refrac=tau_refrac, i_offset=i_offset, v_init=v_init,
            # global for all devices that this control module works with
            uart_id=uart_id,
            # neuron_ids for devices
            motor_0_permanent_velocity_neuron_id=
            motor_0_permanent_velocity_neuron_id,
            motor_0_leaky_velocity_neuron_id=motor_0_leaky_velocity_neuron_id,
            motor_1_permanent_velocity_neuron_id=
            motor_1_permanent_velocity_neuron_id,
            motor_1_leaky_velocity_neuron_id=motor_1_leaky_velocity_neuron_id,
            laser_total_period_neuron_id=laser_total_period_neuron_id,
            speaker_total_period_neuron_id=speaker_total_period_neuron_id,
            leds_total_period_neuron_id=leds_total_period_neuron_id,
            laser_active_time_neuron_id=laser_active_time_neuron_id,
            speaker_active_time_neuron_id=speaker_active_time_neuron_id,
            front_led_active_time_neuron_id=front_led_active_time_neuron_id,
            back_led_active_time_neuron_id=back_led_active_time_neuron_id,
            speaker_tone_frequency_neuron_id=speaker_tone_frequency_neuron_id,
            speaker_melody_neuron_id=speaker_melody_neuron_id,
            laser_frequency_neuron_id=laser_frequency_neuron_id,
            led_frequency_neuron_id=led_frequency_neuron_id
        )
