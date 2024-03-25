#!/usr/bin/env python3

from gnuradio import gr, blocks, uhd
import numpy as np
import matplotlib.pyplot as plt

class CSI_Magnitude_Phase(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        # USRP source parameters
        self.samp_rate = 180e3
        self.center_freq = 3400e6
        self.antenna = "TX/RX"
        self.subdev_spec = 'A:A'

        # Set up USRP source
        self.usrp_source = uhd.usrp_source(
            device_addr='',
            stream_args=uhd.stream_args(
                cpu_format="fc32",
                otw_format="sc16",
                channels=range(1),
            ),
        )
        self.usrp_source.set_samp_rate(self.samp_rate)
        self.usrp_source.set_center_freq(self.center_freq)
        self.usrp_source.set_antenna(self.antenna)
        self.usrp_source.set_subdev_spec(self.subdev_spec)

        # CSI extraction block
        self.csi_extractor = blocks.complex_to_magphase()
        
        #Probe signal Blocks for getting the value
        self.magnitude_out = blocks.probe_signal_f()
        self.phase_out = blocks.probe_signal_f()


        # Connect blocks
        self.connect(self.usrp_source, self.csi_extractor)
        self.connect((self.csi_extractor,0), self.magnitude_out)
        self.connect((self.csi_extractor,1), self.phase_out)

def main():
    tb = CSI_Magnitude_Phase()

    # Start the flow graph
    tb.start()

    try:
        # Collect data for a certain time or until interrupted
        while True:
            # mag_phase = tb.csi_extractor
            # Process the magnitude and phase data here as needed
            magnitude = tb.magnitude_out.level()
            phase = tb.phase_out.level()

            # Example: Print magnitude and phase
            print("Magnitude:", magnitude)
            print("Phase:", phase)

    except KeyboardInterrupt:
        # Stop the flow graph
        tb.stop()
        tb.wait()

if __name__ == '__main__':
    main()  