#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py
Author: "Shams Bin Harun"
Semester: "Fall 2024"

The python code in this file is original work written by
"Shams Bin Harun". No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or on-line resource. I have not shared this python script
with anyone or anything except for submission for grading.
I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: This program displays system memory usage or memory usage of 
specific processes in a user-friendly way using bar charts.
'''

import argparse
import os
import sys


def parse_command_args() -> object:
    """Set up argparse to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Memory Visualiser -- See Memory Usage Report with bar charts",
        epilog="Copyright 2023"
    )
    parser.add_argument("-H", "--human-readable", action="store_true",
                        help="Prints sizes in human-readable format")
    parser.add_argument("-l", "--length", type=int, default=20,
                        help="Specify the length of the graph. Default is 20.")
    parser.add_argument("program", type=str, nargs='?',
                        help="If a program is specified, show memory use of all associated processes. Show only total use if not.")
    return parser.parse_args()


def percent_to_graph(percent: float, length: int = 20) -> str:
    """ Converts a percentage into a graphical bar representation.
    Args: percent (float): A percentage value (0-100).length (int): Total length of the graph (default is 20).
    Returns:str: A string representing the graph. """
   
 # Calculate the number of '#' symbols based on the percentage
    num_hashes = round((percent / 100) * length)
 # Create the graph: '#' repeated num_hashes times, followed by spaces
    graph = '#' * num_hashes + ' ' * (length - num_hashes)
    return graph


def get_sys_mem() -> int:
    """Returns the total system memory (in kB) from /proc/meminfo."""
    with open('/proc/meminfo', 'r') as meminfo:
        for line in meminfo:
            if line.startswith("MemTotal"):
                total_mem_kb = int(line.split()[1])
                return total_mem_kb
    return 0


def get_avail_mem() -> int:
    """Returns the available memory (in kB) from /proc/meminfo."""
    with open('/proc/meminfo', 'r') as meminfo:
        for line in meminfo:
            if line.startswith("MemAvailable"):
                available_mem_kb = int(line.split()[1])
                return available_mem_kb
    return 0

def pids_of_prog(program: str) -> list:
    """Returns a list of process IDs (pids) for the given program."""
    """ Uses os.popen to execute the pidof command and capture the output """
    output = os.popen(f"pidof {program}").read()
    """ Split the output string into a list of pids, strip any excess whitespace """
    pids = output.strip().split()
    return pids


def rss_mem_of_pid(proc_id: str) -> int:
    """Returns the RSS memory usage (in kB) for a given PID."""
    rss_mem = 0
    try:
        with open(f'/proc/{proc_id}/smaps', 'r') as smaps:
            for line in smaps:
                if line.startswith("Rss"):
                    rss_mem += int(line.split()[1])
    except FileNotFoundError:
        return 0
    return rss_mem


def bytes_to_human_r(kibibytes: int, decimal_places: int = 2) -> str:
    """Converts bytes to a human-readable format."""
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suf_count = 0
    result = kibibytes
    while result > 1024 and suf_count < len(suffixes) - 1:
        result /= 1024
        suf_count += 1
    return f'{result:.{decimal_places}f} {suffixes[suf_count]}'


if __name__ == "__main__":
    args = parse_command_args()

    """ Gets total and available system memory """
    total_mem_kb = get_sys_mem()
    available_mem_kb = get_avail_mem()
    used_mem_kb = total_mem_kb - available_mem_kb
    mem_percent = used_mem_kb / total_mem_kb

    if not args.program:
        """ No program argument, show total memory usage """
        print(f"Memory {percent_to_graph(mem_percent, args.length)} {used_mem_kb}/{total_mem_kb}")
        if args.human_readable:
            print(f"Memory {percent_to_graph(mem_percent, args.length)} {bytes_to_human_r(used_mem_kb)}/{bytes_to_human_r(total_mem_kb)}")
    else:
        """ Shows memory usage of specific program's processes """
        pids = pids_of_prog(args.program)
        total_rss = 0
        for pid in pids:
            rss = rss_mem_of_pid(pid)
            total_rss += rss
            print(f"{pid} {percent_to_graph(rss / total_mem_kb, args.length)} {rss}/{total_mem_kb}")
        if pids:
            print(f"{args.program}{percent_to_graph(total_rss / total_mem_kb, args.length)} {total_rss}/{total_mem_kb}")
        else:
            print(f"No processes found for {args.program}.")
