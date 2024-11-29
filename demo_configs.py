# Copyright 2024 D-Wave
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This file stores input parameters for the app."""

# THEME_COLOR is used for the button, text, and banner and should be dark
# and pass accessibility checks with white: https://webaim.org/resources/contrastchecker/
# THEME_COLOR_SECONDARY can be light or dark and is used for sliders, loading icon, and tabs
THEME_COLOR = "#074C91"  # D-Wave dark blue default #074C91
THEME_COLOR_SECONDARY = "#2A7DE1"  # D-Wave blue default #2A7DE1

THUMBNAIL = "static/dwave_logo.svg"

APP_TITLE = "VM Load Balancing"
MAIN_HEADER = "VM Load Balancing"
DESCRIPTION = """\
Virtual machine load balancing is the problem of distributing virtual machines in a way that
evenly balances CPU and memory requirements across a set of hosts, preventing overload
or under-utilization of host machines. 
"""

RANDOM_SEED = None

# Both caps must be larger than the max hosts.
MEMORY_CAP = 1026
MEMORY_UNITS = "GiB"
CPU_CAP = 167
CPU_UNITS = "GHz"

#######################################
# Sliders, buttons and option entries #
#######################################

# an example slider
VMS = {
    "min": 100,
    "max": 500,
    "step": 1,
    "value": 100,
}

HOSTS = {
    "min": 5,
    "max": 30,
    "step": 1,
    "value": 10,
}

# solver time limits in seconds (value means default)
SOLVER_TIME = {
    "min": 10,
    "max": 300,
    "step": 5,
    "value": 10,
}
