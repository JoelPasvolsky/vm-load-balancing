import unittest

from dimod import BINARY

from demo_configs import CPU_CAP, MEMORY_CAP
from src import cqm_balancer
from src.demo_enums import PriorityType


class TestCqmBalancer(unittest.TestCase):
    def test_format_results(self):
        """Test if plan data can be converted into results"""
        vms = {
            "VM 1": {
                "status": "Running",
                "current_host": "Host 1",
                "cpu": CPU_CAP / 4,
                "mem": MEMORY_CAP / 4,
            },
            "VM 2": {
                "status": "Running",
                "current_host": "Host 2",
                "cpu": CPU_CAP / 4,
                "mem": MEMORY_CAP / 4,
            },
            "VM 3": {
                "status": "Running",
                "current_host": "Host 2",
                "cpu": CPU_CAP / 2,
                "mem": MEMORY_CAP / 2,
            },
        }

        hosts = {
            "Host 1": {
                "processor_type": "CPU",
                "cpu_used": CPU_CAP / 4,
                "mem_used": MEMORY_CAP / 4,
                "cpu_cap": CPU_CAP,
                "mem_cap": MEMORY_CAP,
            },
            "Host 2": {
                "processor_type": "CPU",
                "cpu_used": CPU_CAP * 3 / 4,
                "mem_used": MEMORY_CAP * 3 / 4,
                "cpu_cap": CPU_CAP,
                "mem_cap": MEMORY_CAP,
            },
        }

        plan = [
            "VM 1_on_Host 1",
            "VM 2_on_Host 1",
            "VM 3_on_Host 2",
        ]

        new_hosts, new_vms = cqm_balancer.format_results(plan, vms, hosts)

        # Check that the correct vms and hosts were returned
        self.assertEqual(vms.keys(), new_vms.keys())
        self.assertEqual(hosts.keys(), new_hosts.keys())

        # Check that VM 2 has been moved to Host 1
        self.assertEqual(new_vms["VM 2"]["current_host"], "Host 1")

        # Check that the system is now balanced
        self.assertEqual(new_hosts["Host 1"]["cpu_used"], new_hosts["Host 2"]["cpu_used"])
        self.assertEqual(new_hosts["Host 1"]["mem_used"], new_hosts["Host 2"]["mem_used"])

    def test_build_cqm(self):
        """Test building the cqm model"""
        vms = {
            "VM 1": {
                "status": "Running",
                "current_host": "Host 1",
                "cpu": CPU_CAP / 4,
                "mem": MEMORY_CAP / 4,
            },
            "VM 2": {
                "status": "Running",
                "current_host": "Host 1",
                "cpu": CPU_CAP / 4,
                "mem": MEMORY_CAP / 4,
            },
            "VM 3": {
                "status": "Running",
                "current_host": "Host 2",
                "cpu": CPU_CAP / 2,
                "mem": MEMORY_CAP / 2,
            },
        }

        hosts = {
            "Host 1": {
                "processor_type": "CPU",
                "cpu_used": CPU_CAP / 2,
                "mem_used": MEMORY_CAP / 2,
                "cpu_cap": CPU_CAP,
                "mem_cap": MEMORY_CAP,
            },
            "Host 2": {
                "processor_type": "CPU",
                "cpu_used": CPU_CAP / 2,
                "mem_used": MEMORY_CAP / 2,
                "cpu_cap": CPU_CAP,
                "mem_cap": MEMORY_CAP,
            },
        }

        cqm = cqm_balancer.build_cqm(vms, hosts, PriorityType(0))

        # Check number of binary variables
        num_binaries = sum(cqm.vartype(v) is BINARY for v in cqm.variables)
        self.assertEqual(num_binaries, len(hosts) * len(vms))

        # Check number of linear constraints
        num_linear_constraints = sum(
            constraint.lhs.is_linear() for constraint in cqm.constraints.values()
        )
        self.assertEqual(num_linear_constraints, len(hosts) * len(vms) + 1)
