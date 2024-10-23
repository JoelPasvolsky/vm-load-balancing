import unittest

from demo_configs import CPU_CAP, MEMORY_CAP
from src import generate_data
from src.demo_enums import PriorityType


class TestGenerateData(unittest.TestCase):
    def test_generate_vms(self):
        """Test virtual machine data generation"""
        num_hosts = 5
        num_vms = 30

        vms = generate_data.generate_vms(num_vms, num_hosts)

        # Check the correct number of vms were created
        self.assertEqual(len(vms), num_vms)

        # Check the correct number of hosts are assigned
        unique_hosts = {vm["current_host"] for vm in vms.values()}
        self.assertEqual(len(unique_hosts), num_hosts)

        # Check no host assignment exceeds capacity
        total_cpu = {vm["current_host"]: 0 for vm in vms.values()}
        total_mem = {vm["current_host"]: 0 for vm in vms.values()}
        for vm in vms.values():
            total_cpu[vm["current_host"]] += vm["cpu"]
            total_mem[vm["current_host"]] += vm["mem"]

        for cpu in total_cpu.values():
            self.assertLessEqual(cpu, CPU_CAP)

        for mem in total_mem.values():
            self.assertLessEqual(mem, MEMORY_CAP)

    def test_generate_hosts(self):
        """Test host data generation"""
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
        num_hosts = 2

        hosts = generate_data.generate_hosts(num_hosts, vms)

        # Check the correct number of hosts were created
        self.assertEqual(len(hosts), num_hosts)

        # Check each host has not exceeded capacity
        for host in hosts.values():
            self.assertLessEqual(host["cpu_used"], host["cpu_cap"])
            self.assertLessEqual(host["mem_used"], host["mem_cap"])

    def test_calculate_cluster_balance_factor(self):
        """Test cluster balance factor calculation"""
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
                "cpu_used": CPU_CAP,
                "mem_used": MEMORY_CAP,
                "cpu_cap": CPU_CAP,
                "mem_cap": MEMORY_CAP,
            },
        }

        priority = PriorityType(0)

        cluster_balance_factor = generate_data.calculate_cluster_balance_factor(hosts, priority)

        self.assertEqual(cluster_balance_factor, 0.5)
