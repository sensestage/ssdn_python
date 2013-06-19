// ============================================
// SuperCollider Code to work with MiniHiveOSC
// ============================================

// check SC's osc port (use as argument for minihiveosc
NetAddr.langPort;

// in 3.4:
~o1 = OSCresponderNode( nil, "/minibee/data", { |t,r,msg| msg.postln; } ).add;
~o2 = OSCresponderNode( nil, "/minibee/info", { |t,r,msg| msg.postln; } ).add;
~o3 = OSCresponderNode( nil, "/minibee/status", { |t,r,msg| msg.postln; } ).add;

// in 3.5.~dev:
OSCdef( \minibeedata, { |data,time,src|  data.postln; }, '/minibee/data' );
OSCdef( \minibeeinfo, { |data,time,src| [data,time,src].postln; }, '/minibee/info' );
OSCdef( \minibeestatus, { |data,time,src| [data,time,src].postln; }, '/minibee/status' );


n = NetAddr.new( "127.0.0.1" , 57600 );


// set output to the minibee:
n.sendMsg( "/minibee/output", 1, 255 ); // arguments: minibee ID, value of the led output
// number of values you send needs to match the number of outputs you defined:
// the order of the values:
// first PWM / AnalogOut pins (D9)
// first DigitalOut pins (D3)



// set output to the minibee:
n.sendMsg( "/minibee/output", 1, 255, 255, 255 );
n.sendMsg( "/minibee/output", 1, 0,0,0 );

n.sendMsg( "/minibee/output", 1, 255,255,0 );
n.sendMsg( "/minibee/output", 1, 255,0,255 );
n.sendMsg( "/minibee/output", 1, 0,255,255 );

n.sendMsg( "/minibee/output", 1, 255,0,0 );

n.sendMsg( "/minibee/output", 1, 200,255,0 );


// turn minibee data sending off:
n.sendMsg( "/minibee/run", 1, 0 );
// turn minibee data sending on:
n.sendMsg( "/minibee/run", 1, 1 );


// set configuration to a minibee:
n.sendMsg( "/minibee/configuration", 1, 1 ); // minibee id, config id
n.sendMsg( "/minibee/configuration", 2, 1 ); // minibee id, config id
n.sendMsg( "/minibee/configuration", 3, 1 ); // minibee id, config id
n.sendMsg( "/minibee/configuration", 4, 1 ); // minibee id, config id
n.sendMsg( "/minibee/configuration", 5, 1 ); // minibee id, config id

// define configuration:

// (10) id for configuration
// ("testconfig") name/label for configuration
// (1) samples per message
// (25) message interval in ms
// (2) number of pins that I will define in this configuration
// (1) number of twi devices that I will define in this configuration
// (A1) pin id
// (AnalogIn) pin function (analog input)
// (licht) label for the pin
// (D11) pin id
// (DigitalIn) pin function (digital input)
// (beweging) label for the pin
// (ADXL345) first TWI device
// (versnelling) label for the twi device
n.sendMsg( "/minihive/configuration/create", 10, "testconfig", 1, 25, 2, 1, 'A1', 'AnalogIn', 'licht', 'D11', 'DigitalIn', 'beweging', 1, 'ADXL345', 'versnelling' );


// set configuration to a minibee:
n.sendMsg( "/minibee/configuration", 1, 10 ); // minibee id, config id


// saving and loading:
n.sendMsg( "/minihive/configuration/save", "rmhiveconfig.xml");
n.sendMsg( "/minihive/configuration/load", "rmhiveconfig.xml");


// queries are not yet implemented by minihiveosc:
//n.sendMsg( "/minihive/configuration/query", 1 );
//n.sendMsg( "/minihive/configuration/pin/query", 1, 'A1' );
//n.sendMsg( "/minihive/configuration/twi/query", 1, 1 );


// pin by pin, twi by twi configuration:
n.sendMsg( "/minihive/configuration/pin", 1, 'A1', 'AnalogIn', 'Light');
n.sendMsg( "/minihive/configuration/twi", 1, 1, 'TMP102', 'Temperature');
n.sendMsg( "/minihive/configuration/twi", 1, 2, 'ADXL345', 'Versnelling');

n.sendMsg( "/minihive/configuration/pin", 1, 'A1', 1, 'Light');
n.sendMsg( "/minihive/configuration/twi", 1, 2, 1, 'Versnelling');


///---- advanced functions:

// reset minibee:
n.sendMsg( "/minibee/reset", 1 );

// send announce to minibee:
n.sendMsg( "/minibee/announce", 1 );

// save id of minibee in xbee:
n.sendMsg( "/minibee/saveid", 1 );

// save all ids of active minibees in the network in xbee:
n.sendMsg( "/minihive/ids/save" );

// reset all active minibees in the network:
n.sendMsg( "/minihive/reset" );


// mini hive junxion:
~o4 = OSCresponderNode( nil, "/minibee/data/1", { |t,r,msg| msg.postln; } ).add;

Tdef( \x,{ loop{
	n.sendMsg( "/jXcontrol/1", 0.54);
	0.1.wait;
}});
Tdef( \x ).stop
