"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr

class csi_calculator(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="CSI Calculator",
            in_sig=[np.complex64],
            out_sig=[np.float32, np.float32, np.float32])
    
    def calculate_snr(self, signal, noise):
        signal_power = np.mean(np.abs(signal)**2)
        noise_power = np.mean(np.abs(noise)**2)
        snr = 10 * np.log10(signal_power / noise_power)
        return snr
    
    def estimate_doppler_shift(self, received_signal, sample_rate):
        frequency_spectrum = np.fft.fft(received_signal)
        frequency_bins = np.fft.fftfreq(len(received_signal), d=1/sample_rate)
        peak_index = np.argmax(np.abs(frequency_spectrum))
        doppler_shift = frequency_bins[peak_index]
        return doppler_shift
    
    def calculate_delay_spread(self, received_signal, sample_rate):
        correlation = np.correlate(received_signal, received_signal, mode='full')
        power_delay_profile = np.abs(correlation)**2
        delay_indices = np.arange(len(power_delay_profile)) / sample_rate
        mean_delay = np.sum(delay_indices * power_delay_profile) / np.sum(power_delay_profile)
        mean_square_delay = np.sum((delay_indices**2) * power_delay_profile) / np.sum(power_delay_profile)
        delay_spread = np.sqrt(mean_square_delay - mean_delay**2)
        return delay_spread
    
    def work(self, input_items, output_items):
        received_signal = input_items[0]
        noise = received_signal - np.mean(received_signal)  
        
        snr = self.calculate_snr(received_signal, noise)
        doppler_shift = self.estimate_doppler_shift(received_signal, sample_rate=25e6) 
        delay_spread = self.calculate_delay_spread(received_signal, sample_rate=25e6)  
        
        output_items[0][:] = snr
        output_items[1][:] = doppler_shift
        output_items[2][:] = delay_spread
        return len(output_items[0])



gr.basic_block_csi_calculator = csi_calculator
