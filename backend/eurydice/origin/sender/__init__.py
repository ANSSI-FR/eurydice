"""
The sender operates as a service distinct from the origin API and is responsible for
listening to the database for new TransferableRanges and sending them to a Lidis
instance to be transferred through the diode.

It is intended to be run by calling its main.py module, a `run-sender` command is
available in the Makefile and it is advised to use it.
"""
