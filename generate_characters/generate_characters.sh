#!/bin/bash

gap --nointeract gap_compute_characters_symmetric_group.g > gap.out
./parse_gap_output.py gap.out
# rm gap.out
