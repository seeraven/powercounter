PowerCounter
============

Python based application to analyze the data of a electricity meter sent over
an infrared LED using an USB UART adapter. The extracted data is sent via MQTT.


Hardware Interface
------------------

The hardware interface consists of a USB to TTL adapter using a CP2102, an
SFH 309FA-4 infrared photo transistor and a 1.5kOhm resistor:

```
                +----------------+--5V-->
USB Port <----> | CP2102 Adapter |--RxD->
                +----------------+--GND->

  5V----+
        |
       ---
       | | 1.5kOhm
       ---
        |
  RxD---+
        |
      |/   SFH 309FA-4
      |\
        |
  GND---+
```


Installation
------------

powercounter is distributed as a single executable packaged using [pyInstaller].
So all you have to do is to download the latest executable and copy it to a
location of your choice, for example `/usr/local/bin`:

    wget https://github.com/seeraven/powercounter/releases/download/v1.0.0/powercounter_Ubuntu18.04_amd64
    chmod +x powercounter_Ubuntu18.04_amd64
    sudo mv powercounter_Ubuntu18.04_amd64 /usr/local/bin/powercounter


Debugging the Protocol
----------------------

For debugging the raw protocol sent over the serial line, you can first capture
a data file by calling:

    powercounter -c raw_data.dat

And then analyse it by using it as an input file:

    powercounter -i raw_data.dat


[pyInstaller]: https://www.pyinstaller.org/
