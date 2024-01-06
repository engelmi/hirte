# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import time
from typing import Dict

from bluechi_test.util import read_file
from bluechi_test.test import BluechiTest
from bluechi_test.container import BluechiControllerContainer, BluechiNodeContainer
from bluechi_test.config import BluechiControllerConfig, BluechiNodeConfig


node_one = "node-1"
node_two = "node-2"
node_three = "node-3"
nodes = [node_one, node_two, node_three]


def stop_all_agents(nodes: Dict[str, BluechiControllerContainer]):
    for node_name, node in nodes.items():
        result, output = node.exec_run("systemctl stop bluechi-agent")
        if result != 0:
            raise Exception(f"Failed to stop bluechi-agent on node '{node_name}': {output}")


def start_all_agents(nodes: Dict[str, BluechiControllerContainer]):
    for node_name, node in nodes.items():
        result, output = node.exec_run("systemctl start bluechi-agent")
        if result != 0:
            raise Exception(f"Failed to stop bluechi-agent on node '{node_name}': {output}")


def exec(ctrl: BluechiControllerContainer, nodes: Dict[str, BluechiNodeContainer]):

    ctrl.create_file("/tmp", "system-monitor.py", read_file("python/system-monitor.py"))
    ctrl.copy_systemd_service("monitor.service", "systemd", os.path.join("/", "etc", "systemd", "system"))

    result, output = ctrl.exec_run("systemctl start monitor.service")
    if result != 0:
        raise Exception(f"Failed to start monitor service: {output}")

    # wait a bit so monitor is set up
    time.sleep(2)

    stop_all_agents(nodes)

    # wait a bit to process all events
    time.sleep(1)

    result, output = ctrl.exec_run("cat /tmp/events")
    if result != 0:
        raise Exception(f"Failed to get events file: {output}")

    assert output == "degraded,down,"

    start_all_agents(nodes)

    # wait a bit to process all events
    time.sleep(1)

    result, output = ctrl.exec_run("cat /tmp/events")
    if result != 0:
        raise Exception(f"Failed to get events file: {output}")

    assert output == "degraded,down,degraded,up,"


def test_monitor_system_status(
        bluechi_test: BluechiTest,
        bluechi_ctrl_default_config: BluechiControllerConfig,
        bluechi_node_default_config: BluechiNodeConfig):

    node_one_config = bluechi_node_default_config.deep_copy()
    node_one_config.node_name = node_one
    node_two_config = bluechi_node_default_config.deep_copy()
    node_two_config.node_name = node_two
    node_three_config = bluechi_node_default_config.deep_copy()
    node_three_config.node_name = node_three

    bluechi_ctrl_default_config.allowed_node_names = nodes

    bluechi_test.set_bluechi_controller_config(bluechi_ctrl_default_config)
    bluechi_test.add_bluechi_node_config(node_one_config)
    bluechi_test.add_bluechi_node_config(node_two_config)
    bluechi_test.add_bluechi_node_config(node_three_config)

    bluechi_test.run(exec)
