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
from dimod import Binary, ConstrainedQuadraticModel, quicksum
from dwave.system import LeapHybridCQMSampler

from src.demo_enums import PriorityType


def format_results(
    plan: list[str], vms: dict[dict], hosts: dict[dict]
) -> tuple[dict[dict], dict[dict]]:
    """Transform a list of results into a dict pairing virtual machines with hosts.

    Args:
        vms_on_hosts: A list of strings where each string has the form ``vm_on_host``.
        vms: A dict of virtual machine dictionaries.
        hosts: A dict of host dictionaries.

    Returns:
        dict[dict]: The updated host dictionaries.
        dict[dict]: The updated virtual machine dictionaries.
    """
    for host in hosts:
        hosts[host]["cpu_used"] = 0
        hosts[host]["mem_used"] = 0

    for assignment in plan:
        vm_id, host_assignment = assignment.split("_on_")
        vm = vms[vm_id]

        hosts[host_assignment]["cpu_used"] += vm["cpu"]
        hosts[host_assignment]["mem_used"] += vm["mem"]

        vms[vm_id]["current_host"] = host_assignment

    return hosts, vms


def build_cqm(
    vms: dict[dict], hosts: dict[dict], priority: PriorityType
) -> ConstrainedQuadraticModel:
    """Define objectives and constraints of the CQM.

    Args:
        vms: A dict of VM dicts containing current host and cpu and memory use.
        hosts: A dict of host dicts containing the CPU and memory cap as well as
            the current CPU and memory use.
        priority: Whether to prioritize balancing memory or CPU.

    Returns:
        ConstrainedQuadraticModel: The CQM model.
    """
    requested_cpu = {vm_id: vm_data["cpu"] for vm_id, vm_data in vms.items()}
    requested_mem = {vm_id: vm_data["mem"] for vm_id, vm_data in vms.items()}

    total_requested_cpu = sum(requested_cpu.values())
    total_requested_mem = sum(requested_mem.values())

    available_cpu_per_host = {host_id: host_data["cpu_cap"] for host_id, host_data in hosts.items()}
    available_mem_per_host = {host_id: host_data["mem_cap"] for host_id, host_data in hosts.items()}

    total_available_cpu = sum(available_cpu_per_host.values())
    total_available_mem = sum(available_mem_per_host.values())

    # Objective: balance use across hosts

    balanced_cpu = {
        host: host_cpu * total_requested_cpu / total_available_cpu
        for host, host_cpu in available_cpu_per_host.items()
    }
    balanced_mem = {
        host: host_mem * total_requested_mem / total_available_mem
        for host, host_mem in available_mem_per_host.items()
    }

    cqm = ConstrainedQuadraticModel()

    sum_cpu = {}
    sum_mem = {}
    for host in available_cpu_per_host:
        sum_cpu[f"cpu_{host}"] = quicksum(
            requested_cpu[vm] * Binary(f"{vm}_on_{host}") for vm in requested_cpu
        )
        sum_mem[f"mem_{host}"] = quicksum(
            requested_mem[vm] * Binary(f"{vm}_on_{host}") for vm in requested_mem
        )

    for host in available_cpu_per_host:
        if priority is PriorityType.CPU:
            # Set CPU balancing as a hard constraint, memory balancing as a soft constraint.
            cqm.add_constraint(
                sum_cpu[f"cpu_{host}"] <= balanced_cpu[host],
                label=f"cpu_{host}",
                penalty="quadratic",
            )
            cqm.add_constraint(
                sum_mem[f"mem_{host}"] <= balanced_mem[host],
                label=f"mem_{host}",
                penalty="quadratic",
                weight=1,
            )
        else:
            # Set memory balancing as a hard constraint, CPU balancing as a soft constraint.
            cqm.add_constraint(
                sum_cpu[f"cpu_{host}"] <= balanced_cpu[host],
                label=f"cpu_{host}",
                penalty="quadratic",
                weight=1,
            )
            cqm.add_constraint(
                sum_mem[f"mem_{host}"] <= balanced_mem[host],
                label=f"mem_{host}",
                penalty="quadratic",
            )

    # Ensure that each vm is only assigned to one host with one hot constraint.
    for vm in requested_cpu:
        cqm.add_discrete(
            [f"{vm}_on_{host}" for host in available_cpu_per_host], label=f"discrete_{vm}"
        )

    return cqm


def get_solution(cqm: ConstrainedQuadraticModel, time_limit: int) -> list[str]:
    """Call CQM solver and format results.

    Args:
        cqm: The CQM model.
        time_limit: Time limit (in second) to run the problem for.

    Returns:
        list[str]: A list of strings pairing virtual machines and hosts.
    """
    sampler = LeapHybridCQMSampler()
    sampleset = sampler.sample_cqm(cqm, time_limit=time_limit, label="VM Balancing Demo")

    best_result = sampleset.first.sample

    result = [k for k, v in best_result.items() if v == 1]

    return result
