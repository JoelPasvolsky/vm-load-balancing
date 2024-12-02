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

import math
import random

from demo_configs import CPU_CAP, MEMORY_CAP, RANDOM_SEED
from src.demo_enums import PriorityType


def generate_resource_use(num_vms: int, total_resource: list[int]) -> list[float]:
    """Generates a random list of virtual machine resource use for a given number of VMs.

    Args:
        num_vms: The number of virtual machines assigned to this host.
        total_resource: The amount of resource this host has allocated to its' VMs.

    Returns:
        list[float]: A dict of VM resource assignments where the index+1 is the VM id.
    """
    random_floats = [random.random() for _ in range(num_vms)]
    scale_resource = total_resource / sum(random_floats)
    resource_use = [rand_float * scale_resource for rand_float in random_floats]
    return resource_use


def generate_vms(total_vms: int, total_hosts: int) -> dict[dict]:
    """Generates a dict of random virtual machine dictionaries containing current host and cpu and
        memory use. Specifically aims at creating an unbalanced system with VMs with a variety of
        CPU and memory use and a variety of host utilization.

    Args:
        total_vms: The total number of virtual machines to be assigned to hosts.
        total_hosts: The total number of available hosts.

    Returns:
        dict[dict]: A dict of VM dicts containing current host and cpu and memory use.
    """
    random.seed(RANDOM_SEED)

    # force each host to have at least base_vm_count VMs
    base_vm_count = math.floor(total_vms / (2 * total_hosts))
    remaining_vms = total_vms - (base_vm_count * total_hosts)

    # Divide total_vms into total_hosts parts
    divides = (
        [0] + sorted(random.sample(range(1, remaining_vms), total_hosts - 1)) + [remaining_vms]
    )
    vms_per_host = [divides[i + 1] - divides[i] + base_vm_count for i in range(total_hosts)]

    # Get cpu/memory use per host, use step size of 3 to help create unbalance.
    total_cpu = random.sample(range(math.ceil(CPU_CAP * 0.25), math.floor(CPU_CAP), 3), total_hosts)
    total_memory = random.sample(
        range(math.ceil(MEMORY_CAP * 0.25), math.floor(MEMORY_CAP), 3), total_hosts
    )

    vms = {}
    vm_count = 1
    for host, num_vms in enumerate(vms_per_host):
        host_name = f"Host {host+1}"
        cpu_use = generate_resource_use(num_vms, total_cpu[host])
        mem_use = generate_resource_use(num_vms, total_memory[host])

        for cpu, mem in zip(cpu_use, mem_use):
            vms[f"VM {vm_count}"] = {
                "status": "Running",
                "current_host": host_name,
                "cpu": cpu,
                "mem": mem,
            }
            vm_count += 1

    return vms


def generate_hosts(total_hosts: int, vms: dict[dict]) -> dict[dict]:
    """Generates a dict of random host dictionaries containing the CPU and memory cap as well as
        the current CPU and memory use.

    Args:
        total_hosts: The total number of available hosts.
        vms: A dict of VM dicts containing current host and cpu and memory use.

    Returns:
        dict[dict]: A dict of host dicts containing the CPU and memory cap as well as
        the current CPU and memory use.
    """
    hosts = {}
    cpu_used = [0] * total_hosts
    mem_used = [0] * total_hosts
    for vm in vms.values():
        host_index = int(vm["current_host"].split(" ")[1]) - 1
        cpu_used[host_index] += vm["cpu"]
        mem_used[host_index] += vm["mem"]

    for host, (cpu, mem) in enumerate(zip(cpu_used, mem_used)):
        hosts[f"Host {host+1}"] = {
            "processor_type": "CPU",
            "cpu_used": cpu,
            "mem_used": mem,
            "cpu_cap": CPU_CAP,
            "mem_cap": MEMORY_CAP,
        }

    return hosts


def calculate_cluster_balance_factor(
    hosts: dict[dict], priority: PriorityType, priority_weight: int = 10
) -> float:
    """Calculates the cluster balance factor, which is a metric created to help evaluate
    the quality of the virtual machine to host assignments.

    Args:
        hosts: A dict of host dictionaries.
        priority: Whether to prioritize balancing memory or CPU.

    Returns:
        float: Cluster balance factor between 0 and 1.0.
    """
    if priority is PriorityType.CPU:
        memory_weight = 1
        cpu_weight = priority_weight
    else:
        memory_weight = priority_weight
        cpu_weight = 1

    # Calculate the range of memory and CPU usage percentages across hosts
    memory_usages = [host["mem_used"] / host["mem_cap"] for host in hosts.values()]
    cpu_usages = [host["cpu_used"] / host["cpu_cap"] for host in hosts.values()]

    memory_range = max(memory_usages) - min(memory_usages)
    cpu_range = max(cpu_usages) - min(cpu_usages)

    # Calculate the balance factor as the minimum of the memory and CPU range factors (inverted)
    balance_factor = (((1 - memory_range) * memory_weight) + ((1 - cpu_range) * cpu_weight)) / (
        cpu_weight + memory_weight
    )

    return balance_factor
