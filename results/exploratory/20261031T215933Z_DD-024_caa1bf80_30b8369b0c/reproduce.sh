#!/bin/sh
set -eu
PYTHONPATH=src python -m distributed_discovery.behavioral_diversity.study --track track-04
