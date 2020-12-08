UART Protocol
-------------

The protocol of the electricity meter uses the Smart Message Language SML_ to
transport the data. The specification of this protocol can be found on BSI-SML_
or explained for electricity meters on `Stefan Weigert - Das SML-Interface`_.

The transferred message is called a SML file, and consists of the following
structure (version 1):

.. code-block:: python

   0x1b 0x1b 0x1b 0x1b  The escape sequence. Here, it marks the begin of the message
   0x01 0x01 0x01 0x01  The version 1 identifier
   <List of SML messages>
   <0 to 3 padding bytes 0x00>
   0x1b 0x1b 0x1b 0x1b  The escape sequence before marking the end of the message
   0x1a   XX   YY   ZZ  End of message. Number of padding bytes = XX, CRC = YY ZZ


The number of padding bytes is chosen so that the whole SML file contains a
multiple of 4 bytes.
If the escape sequence :code:`0x1b1b1b1b` is part of the SML-messages data, it is
escaped with that same sequence. That means that a sequence :code:`0x1b1b1b1b1b1b1b1b`
is reduced to :code:`0x1b1b1b1b` during the decoding. In practice, this can occur if
an integer or unsigned integer value of 32 or 64-bit is encoded or within a so
called octet string.
The CRC at the end of the message is calculated according to CCITT-CRC16 over
all bytes starting with the first escape sequence and ending at the number
of padding bytes element.

The individual elements are encoded using a type-length structure. Here, the
upper 4 bits encode the type and the lower 4 bits encode the length:

  - :code:`0x0L`: Octet string of total length :code:`L` bytes (including the type byte(s))
  - :code:`0x42`: Boolean. Following byte :code:`0x00` encodes false, everything else true
  - :code:`0x5L`: Signed integer: int8 = :code:`0x52`, int16 = :code:`0x53`, int32 = :code:`0x55`, int64 = :code:`0x59`
  - :code:`0x6L`: Unsigned integer: uint8 = :code:`0x62`, uint16 = :code:`0x63`, uint32 = :code:`0x65`, uint64 = :code:`0x69`
  - :code:`0x7L`: List of L entries
  - :code:`0x00`: End of message field

To extend the length, the most significant bit can be set to extend the length by
4 bits. If the following byte has the most significant bit set again, another byte
is used for the length and so on. This makes only sense for the octet string and
eventually the list type. For example, :code:`0x83 02` encodes an octet string
with a length of :code:`0x32` bytes. Again, the type bytes are counted, so the actual
string data is only :code:`0x30` bytes long.

To determine a full SML file, we have to analyze the stream and search for the
sequence :code:`0x1b1b1b1b, 0x01010101`. Then we need to read until we get the end of
the message sequence :code:`0x1b1b1b1b 0x1aXXYYZZ`. Remembering the rules of escaping,
we also need to ensure that the 4 bytes before the escape sequence are not the
escape sequence, otherwise they would encode data.


.. _SML: https://de.wikipedia.org/wiki/Smart_Message_Language
.. _BSI-SML: https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Publikationen/TechnischeRichtlinien/TR03109/TR-03109-1_Anlage_Feinspezifikation_Drahtgebundene_LMN-Schnittstelle_Teilb.pdf?__blob=publicationFile
.. _`Stefan Weigert - Das SML-Interface`: http://www.stefan-weigert.de/php_loader/sml.php
