Architech Design Record
=======================

The aim of this document is to log the architectural decisions made during in the improving of the Venmo example software project. That gives a clear straitforward thiking on how the decisions were taken.

Use of Python's Decimal to represent monatary values
----------------------------------------------------

.. literalinclude:: example.py
   :language: python
   :lines: 33-40
   :emphasize-lines: 37-37


In several parts of the provided example, monetary values are represented using floats. This is not recommended due to the way IEEE 754 stores and manipulates float values for performance. Floats are not precise enough for representing monetary values accurately. IEEE's float representation is not mean to be precise, but fast. Even with more than 32 bits, such errors may arrise.

For example:

.. code:: python

    value = 0.1 + 0.2
    print(0.3 == value) # Outputs: False
    print(value)        # Outputs: 0.30000000000000004


.. code:: python

    value = 100.3 + 0.1
    print(100.4 == value) # Outputs: False
    print(value)          # Outputs: 100.39999999999999


Although, we we use Decimal, we would not face such problem.


Define a double entry account system
------------------------------------

.. literalinclude:: example.py
   :language: python
   :lines: 43-47
   :emphasize-lines: 47

In the original example, "balance" was just a variable that wasn't auditable or able to track changes within the system.

.. literalinclude:: example.py
   :language: python
   :lines: 63-64
   :emphasize-lines: 64

Furthermore, the system might be susceptible to ghost transaction failures when attempting to update the balance while fetching it, due to improper database locking. Overall, update operations are dangerous in such environments.


A monetary system must be accountable; therefore, the "balance" state should be defined by the actual state of all transactions performed. Also, since there are no updates or deletions in the system, it is less susceptible to ghost transaction failures.

Use of well defined types
-------------------------

Username and Credit Card Number are not just string variables; these can be well-defined as distinct types. This approach centralizes the checks and definitions, making the system more robust and isolated.

