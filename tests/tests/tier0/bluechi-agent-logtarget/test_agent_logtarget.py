# SPDX-License-Identifier: LGPL-2.1-or-later

from typing import Dict

from bluechi_test.test import BlueChiTest
from bluechi_test.machine import BlueChiControllerMachine, BlueChiAgentMachine
from bluechi_test.config import BlueChiControllerConfig, BlueChiAgentConfig

NODE_GOOD = "node-good"
NODE_WITH_LONG_LOGTARGET = "node-long-logtarget"
NODE_WITH_NOT_VALID_VALUE = "node-with-not-valid-value"
NODE_WITH_NUMBERS_ONLY_IN_LOGTARGET = "node-numbers-only"


def start_with_invalid_logtarget(ctrl: BlueChiControllerMachine, nodes: Dict[str, BlueChiAgentMachine]):
    node_good = nodes[NODE_GOOD]
    assert node_good.wait_for_unit_state_to_be("bluechi-agent", "active")

    node_with_long_logtarget = nodes[NODE_WITH_LONG_LOGTARGET]
    assert node_with_long_logtarget.wait_for_unit_state_to_be("bluechi-agent", "failed")

    node_with_numbers_only_in_logtarget = nodes[NODE_WITH_NUMBERS_ONLY_IN_LOGTARGET]
    assert node_with_numbers_only_in_logtarget.wait_for_unit_state_to_be("bluechi-agent", "active")

    node_with_not_valid_value = nodes[NODE_WITH_NOT_VALID_VALUE]
    assert node_with_not_valid_value.wait_for_unit_state_to_be("bluechi-agent", "active")


def test_agent_invalid_logtarget_configuration(
        bluechi_test: BlueChiTest,
        bluechi_node_default_config: BlueChiAgentConfig, bluechi_ctrl_default_config: BlueChiControllerConfig):

    node_good_cfg = bluechi_node_default_config.deep_copy()
    node_good_cfg.node_name = NODE_GOOD
    node_good_cfg.log_target = "stderr"

    node_with_long_logtarget_cfg = bluechi_node_default_config.deep_copy()
    node_with_long_logtarget_cfg.node_name = NODE_WITH_LONG_LOGTARGET
    node_with_long_logtarget_cfg.log_target = "NO_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION"  # noqa: E501, E261

    node_with_invalid_value_cfg = bluechi_node_default_config.deep_copy()
    node_with_invalid_value_cfg.node_name = NODE_WITH_NOT_VALID_VALUE
    node_with_invalid_value_cfg.log_target = "NOT_STDERR_OR_JOURNALD_VALUE"

    node_with_numbersonly_in_logtarget_cfg = bluechi_node_default_config.deep_copy()
    node_with_numbersonly_in_logtarget_cfg.node_name = NODE_WITH_NUMBERS_ONLY_IN_LOGTARGET
    node_with_numbersonly_in_logtarget_cfg.log_target = 10000000

    bluechi_ctrl_default_config.allowed_node_names = [
        NODE_GOOD,
        NODE_WITH_LONG_LOGTARGET,
        NODE_WITH_NOT_VALID_VALUE,
        NODE_WITH_NUMBERS_ONLY_IN_LOGTARGET
    ]

    bluechi_test.set_bluechi_ctrl_machine_config(bluechi_ctrl_default_config)

    bluechi_test.add_bluechi_agent_machine_configs(node_good_cfg)
    bluechi_test.add_bluechi_agent_machine_configs(node_with_long_logtarget_cfg)
    bluechi_test.add_bluechi_agent_machine_configs(node_with_invalid_value_cfg)
    bluechi_test.add_bluechi_agent_machine_configs(node_with_numbersonly_in_logtarget_cfg)

    bluechi_test.run(start_with_invalid_logtarget)
