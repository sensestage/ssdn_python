# Pydon hive

Hive manager for the datanetwork in Python.

* INSTALLATION - Detailed installation info is found in the INSTALL file.
* GETTING_STARTED gives a quick overview on how to start with the MiniBees you just got and how to interface with them.
* MINIHIVEOSC_DOCUMENTATION gives an overview of the OSC interface of MiniHiveOsc, one of the ways to interface with the minibees.

[Documentation](https://docs.sensestage.eu)

# CREATING THE CONFIG FILE:

The config file is an xml file.

The top level structure is:

```
<xml>
<hive name="myprojectname">

</hive>
</xml>
```

Then there are elements for each MiniBee you have:

```
  <minibee caps="7" configuration="1" id="1" libversion="5" name="minibee1" revision="D" serial="0013A20040901CB0">
      <custom/>
  </minibee>
```

So the ID, the revision of the board, the serial number of its XBee (see back side of XBee),
the library version and the capabilities are defined. So the elements you want to change are
the id, and the serial number. Optionally, you can define custom inputs on this particular minibee (these would need to be defined in the firmware too)

Then you define the config that is used by this minibee by a number, which refers to a configuration element:

As an example:

```
  <configuration id="2" name="accelero" message_interval="50" samples_per_message="1" redundancy="3">
    <pin config="AnalogIn" id="A0" />
    <pin config="TWIData" id="A4" />
    <pin config="TWIClock" id="A5" />
    <twi id="1" device="ADXL345" />
    <twi id="2" device="TMP102" />
    <twi id="3" device="BMP085" />
  </configuration>
```

So top level:

ID and label
Message interval in milliseconds
Samples per message (for now just use 1)
Redundancy (how often a message is sent out to a minibee)


Then for each pin:
id and configuration. Pins that are not mentioned are not configured.

Possible pin configurations:

`DigitalIn`       -- digital input (any pin but A4, A5, A6, A7)
`DigitalInPullup` -- digital input with pullup resistor enabled (any pin but A4, A5, A6, A7)
`DigitalOut`      -- digital output on/off (any pin but A4, A5, A6, A7)
`AnalogIn`        -- analog input (for pin A0, A1, A2, A3, A6, A7)
`AnalogIn10bit`   -- analog input with 10bit result (for pin A0, A1, A2, A3, A6, A7)
`AnalogOut`       -- PWM or analog out (pins D3, D5, D6, D9, D10, D11)
`Ping`            -- Ultrasonic sensor (any pin but A4, A5, A6, A7)
`SHTClock`        -- Clock signal for SHT15 sensor (temperature/humidity) (any pin but A4, A5, A6, A7)
`SHTData`         -- Data signal for SHT15 sensor (temperature/humidity) (any pin but A4, A5, A6, A7)
`TWIClock`        -- Use a TWI/I2C sensor, clock signal (pin A5)
`TWIData`         -- Use a TWI/I2C sensor, data signal (pin A4)

And if TWI (two-wire interface) is used:
the TWI (or I2C) devices which are used.
Currently supported are ADXL345, LIS302DL, TMP102, BMP085, and HMC58X3.
