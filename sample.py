import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(currentdir)))
from LoRaRF import SX127x

# Begin LoRa radio - initialize SX127x module
# The SX127x handles SPI communication automatically
# GPIO pins are set using setPins() method
LoRa = SX127x()

# Set GPIO pins (reset pin, dio1 pin, txen pin, rxen pin)
# Using GPIO pin numbers: reset=24, others unused (-1)
# Note: CS pin is handled automatically by SPI interface
# Adjust reset_pin if your hardware uses a different GPIO pin
reset_pin = 24
dio1_pin = -1  # Unused
txen_pin = -1  # Unused
rxen_pin = -1  # Unused
LoRa.setPins(reset_pin, dio1_pin, txen_pin, rxen_pin)

print("Begin LoRa radio")
if not LoRa.begin() :
    # You can access the error code using LoRa.getLastError()
    print(f"LoRa begin failed with error code: {LoRa.getLastError()}")
    raise Exception("Something wrong, can't begin LoRa radio")


# Set frequency to 915 Mhz
print("Set frequency to 915 Mhz")
LoRa.setFrequency(915000000)

# Set RX gain. RX gain option are power saving gain or boosted gain
print("Set RX gain to power saving gain")
LoRa.setRxGain(LoRa.RX_GAIN_POWER_SAVING, LoRa.RX_GAIN_AUTO)    # AGC on, Power saving gain

# Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
# Receiver must have same SF and BW setting with transmitter to be able to receive LoRa packet
# Matching Pi Pico settings: radio.begin(915.0, 125.0, 9, 7, RADIOLIB_SX127X_SYNC_WORD, 10, 8, 0)
print("Set modulation parameters:\n\tSpreading factor = 9\n\tBandwidth = 125 kHz\n\tCoding rate = 4/7")
LoRa.setSpreadingFactor(9)                                      # LoRa spreading factor: 9
LoRa.setBandwidth(125000)                                       # Bandwidth: 125 kHz
LoRa.setCodeRate(7)                                             # Coding rate: 4/7

# Configure packet parameter including header type, preamble length, payload length, and CRC type
# The explicit packet includes header contain CR, number of byte, and CRC type
# Receiver can receive packet with different CR and packet parameters in explicit header mode
# With explicit header, payload length is determined from packet header (variable length)
print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 10\n\tVariable payload length\n\tCRC on")
LoRa.setHeaderType(LoRa.HEADER_EXPLICIT)                        # Explicit header mode
LoRa.setPreambleLength(10)                                      # Set preamble length to 10 (matches Pi Pico)
# Don't set fixed payload length - use variable length with explicit header (max 255 bytes)
LoRa.setCrcEnable(True)                                         # Set CRC enable

# Set syncronize word to match RADIOLIB_SX127X_SYNC_WORD (0x12)
print("Set syncronize word to 0x12")
LoRa.setSyncWord(0x12)

print("\n-- LoRa Receiver --\n")

# Receive message continuously
while True :

    # Request for receiving new LoRa packet
    LoRa.request()
    # Wait for incoming LoRa packet
    LoRa.wait()

    # Read all received packet data
    # read() and available() method must be called after request() or listen() method
    message = ""
    # available() method return remaining received payload length and will decrement each read() or get() method called
    while LoRa.available() > 0 :
        message += chr(LoRa.read())

    # Print received message
    print(f"Received: {message}")

    # Print packet/signal status including RSSI, SNR, and signalRSSI
    print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(LoRa.packetRssi(), LoRa.snr()))

    # Show received status in case CRC or header error occur
    status = LoRa.status()
    if status == LoRa.STATUS_CRC_ERR : print("CRC error")
    elif status == LoRa.STATUS_HEADER_ERR : print("Packet header error")