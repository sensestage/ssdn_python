# MINIHIVE OSC documentation

MiniHiveOSC is a simple program which just receives the serial data and sends it to another program via osc, and listens to osc to send data to minibees.
It uses the same configuration file as swpydonhive.

See also [https://docs.sensestage.eu/minibee/osc-interface.html]() for documentation of the interface.

---------------------------------
OSC messages it sends:

* `/minibee/info`      - `siii`   - serial number, id, number of inputs, number of outputs
* `/minibee/data`      - `iff..f` - id, and as many floats as inputs
* `/minibee/private`   - `iff..f` - id, and as many floats as inputs
* `/minibee/trigger`   - `iff..f` - id, and as many floats as inputs
* `/minibee/status`    - `ii`

OSC messages it listens to:

* `/minibee/output`    - `iii..i` - id, and as many 8bit integers as outputs (first PWM's then digital)
* `/minibee/custom`    - `iii..i` - id, and as many 8bit integers as the custom message requires

*pausing a minibee:*

* `/minibee/run`       - `ii` - id, and 0 (for pausing) or 1 (for running)

*debugging a minibee:*

*  `/minibee/loopback` - `ii` - id, and 0 (for not sending messages back) or 1 (for sending each message back)

*resetting a minibee:*

* `/minibee/reset` - `i` - id

* reset all minibees:*

*  `/minihive/reset`

*save id on xbee:*

* `/minibee/saveid` - `i` - id

*save ids of all xbees:*

* `/minihive/ids/save`

*send announce message (re-init):*

* `/minibee/announce` - `i` - id



# ON THE FLY configuration


*assign a config id to a node id, and that to a serial number*

`/minibee/configuration` node id, config id, serial number (optional)

possible return messages:

* `/minibee/configuration/done` node id, config id, serial number (optional)
* `/minibee/configuration/error` node id, config id, serial number (optional)


*load and save config*

`/minihive/configuration/save` filename
`/minihive/configuration/load` filename

*set configuration*

`/minihive/configuration/create`

Format:

* `i` config id
* `s` config name
* `i` samples per message
* `i` message interval
* `i` number of pins defined (N)
* `i` number of TWI devices defined (M)

then N times:

* `s`      - pin id (e.g. A0)
* `s` or `i` - pin function (e.g. 3, or 'AnalogIn')
* `s`      - pin label (e.g. light)

then M times:
* `i`      - twi id (e.g. 0)
* `s` or `i` - twi function (e.g. 10, or 'ADXL345')
* `s`      - twi label (e.g. accelero)

* `/minihive/configuration/short` (as above but without separate pin definitions; those are done separately by the message that follow)
* `/minihive/configuration/pin` config id, pinid, pinconfig
* `/minihive/configuration/twi` config id, twiid, twiconfig

*query configuration*

* `/minihive/configuration/query` config id
* `/minihive/configuration/pin/query` config id, pinid
* `/minihive/configuration/twi/query` config id, twiid



*delete a configuration*

`/minihive/configuration/delete` config id

possible return messages:

* `/minihive/configuration/error` config id
* `/minihive/configuration/delete/done` config id


# TESTING WITH SC or PD

An example of sending the right messages with SuperCollider is given in:

    testminihiveosc.scd

An examples for PureData is given in:

    minihiveosc.pd

