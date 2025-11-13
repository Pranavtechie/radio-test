"""
LoRa Receiver using PyLoRa library
Rewritten from LoRaRF to use PyLoRa (pySX127x) library

Note: This code assumes PyLoRa's default GPIO pin configuration in board_config.py.
If your hardware uses different pins (e.g., reset=22, DIO1=26), you may need to
modify the board_config.py file in the PyLoRa installation directory.
"""
import time
import RPi.GPIO as GPIO
from SX127x.LoRa import LoRa
from SX127x.board_config import BOARD

# Configure GPIO for TX/RX control (matching original receiver.py)
# GPIO pins 5 and 6 are used for TX/RX control
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)

GPIO.output(6, GPIO.LOW)
GPIO.output(5, GPIO.HIGH)

class LoRaReceiver(LoRa):
    def __init__(self, verbose=False):
        super(LoRaReceiver, self).__init__(verbose)
        self.packetData = None
        self.rssi = 0
        self.snr = 0

    def on_rx_done(self):
        """Callback function called when a packet is received"""
        self.clear_irq_flags_rx_done()
        self.packetData = self.read_payload(nocheck=True)
        self.rssi = self.get_pkt_rssi_value()
        self.snr = self.get_pkt_snr_value()
        self.set_mode_rx()

# Initialize LoRa radio
print("Begin LoRa radio")
BOARD.setup()
lora = LoRaReceiver(verbose=False)

# Set frequency to 915 MHz
print("Set frequency to 915 MHz")
lora.set_freq(915.0)  # PyLoRa uses MHz, not Hz

# Set RX gain to boosted gain
# PyLoRa uses set_lna() method for RX gain configuration
print("Set RX gain to boosted gain")
lora.set_lna_gain(lora.LNA_MAX_GAIN)  # Boosted gain
lora.set_lna_boost_hf(True)  # Enable LNA boost for high frequency

# Configure modulation parameters
# Spreading factor (SF), bandwidth (BW), and coding rate (CR)
print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
lora.set_spreading_factor(7)  # Spreading factor: 7
lora.set_bw(125)  # Bandwidth: 125 kHz (PyLoRa uses kHz)
lora.set_coding_rate(5)  # Coding rate: 4/5 (denominator)

# Configure packet parameters
# Header type, preamble length, payload length, and CRC type
print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 255\n\tCRC on")
lora.set_header_mode(lora.HEADER_EXPLICIT)  # Explicit header type
lora.set_preamble(12)  # Preamble length: 12
lora.set_payload_length(255)  # Payload length: 255
lora.set_crc(True)  # Enable CRC

# Set synchronize word for public network (0x34)
print("Set synchronize word to 0x34")
lora.set_sync_word(0x34)

print("\n-- LoRa Receiver --\n")

# Set mode to continuous receive
lora.set_mode(lora.MODE.RXCONT)

# Receive message continuously
try:
    while True:
        # Wait for RX done interrupt (callback will handle packet)
        lora.wait_on_rx()
        
        # Check if packet was received (set by callback)
        if lora.packetData:
            packet = lora.packetData
            
            # Extract message and counter
            # Assuming last byte is counter, rest is message
            if len(packet) > 0:
                length = len(packet) - 1
                message = ""
                for i in range(length):
                    message += chr(packet[i])
                counter = packet[length] if length >= 0 else 0
                
                print(f"{message} {counter}")
                
                # Print packet/signal status including RSSI and SNR
                print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(lora.rssi, lora.snr))
            
            # Clear packet data
            lora.packetData = None

except KeyboardInterrupt:
    print("\nExiting...")
    lora.set_mode(lora.MODE.SLEEP)
    BOARD.teardown()
    GPIO.cleanup()
