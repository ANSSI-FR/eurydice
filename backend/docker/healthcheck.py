#!/usr/local/bin/python
import argparse
import socket

argument_parser = argparse.ArgumentParser(description="Checks if a TCP service is up")
argument_parser.add_argument(
    "-H",
    "--hostname",
    type=str,
    default="localhost",
    nargs="?",
    help="Hostname of the TCP service",
)
argument_parser.add_argument(
    "-p",
    "--port",
    type=int,
    default=8080,
    nargs="?",
    help="Port number of the TCP service",
)
arguments = argument_parser.parse_args()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((arguments.hostname, arguments.port))
