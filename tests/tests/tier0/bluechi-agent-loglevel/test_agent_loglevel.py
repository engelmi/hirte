# SPDX-License-Identifier: LGPL-2.1-or-later

import pytest
from typing import Dict

from bluechi_test.test import BluechiTest
from bluechi_test.container import BluechiControllerContainer, BluechiNodeContainer
from bluechi_test.config import BluechiControllerConfig, BluechiNodeConfig

NODE_GOOD = "node-good"
NODE_WITH_LONG_LOGLEVEL = "node-long-loglevel"
NODE_WITH_NOT_VALID_VALUE = "node-with-not-valid-value"
NODE_WITH_NUMBERS_ONLY_IN_LOGLEVEL = "node-numbers-only"


def start_with_invalid_loglevel(ctrl: BluechiControllerContainer, nodes: Dict[str, BluechiNodeContainer]):

    node_good = nodes[NODE_GOOD]
    assert node_good.wait_for_unit_state_to_be("bluechi-agent", "active")

    node_with_log_loglevel = nodes[NODE_WITH_LONG_LOGLEVEL]
    assert node_with_log_loglevel.wait_for_unit_state_to_be("bluechi-agent", "failed")

    node_with_not_valid_value = nodes[NODE_WITH_NOT_VALID_VALUE]
    assert node_with_not_valid_value.wait_for_unit_state_to_be("bluechi-agent", "active")

    node_with_numbers_only_in_loglevel = nodes[NODE_WITH_NUMBERS_ONLY_IN_LOGLEVEL]
    assert node_with_numbers_only_in_loglevel.wait_for_unit_state_to_be("bluechi-agent", "active")


@pytest.mark.timeout(25)
def test_agent_invalid_configuration(
        bluechi_test: BluechiTest,
        bluechi_node_default_config: BluechiNodeConfig, bluechi_ctrl_default_config: BluechiControllerConfig):

    node_good_cfg = bluechi_node_default_config.deep_copy()
    node_good_cfg.node_name = NODE_GOOD
    node_good_cfg.log_level = "INFO"

    node_with_long_loglevel_cfg = bluechi_node_default_config.deep_copy()
    node_with_long_loglevel_cfg.node_name = NODE_WITH_LONG_LOGLEVEL
    node_with_long_loglevel_cfg.log_level = "NO_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION_NOT_REALLY_A_VALID_OPTION" # noqa: E501, E261

    node_with_invalid_value_cfg = bluechi_node_default_config.deep_copy()
    node_with_invalid_value_cfg.node_name = NODE_WITH_NOT_VALID_VALUE
    node_with_invalid_value_cfg.log_level = "NOT_INFO_OR_DEBUG_OR_WARN_OR_ERROR_VALUE"

    node_with_numbersonly_in_loglevel_cfg = bluechi_node_default_config.deep_copy()
    node_with_numbersonly_in_loglevel_cfg.node_name = NODE_WITH_NUMBERS_ONLY_IN_LOGLEVEL
    node_with_numbersonly_in_loglevel_cfg.log_level = 10000000

    bluechi_ctrl_default_config.allowed_node_names = [
            NODE_GOOD,
            NODE_WITH_LONG_LOGLEVEL,
            NODE_WITH_NOT_VALID_VALUE,
            NODE_WITH_NUMBERS_ONLY_IN_LOGLEVEL
    ]

    bluechi_test.set_bluechi_controller_config(bluechi_ctrl_default_config)

    bluechi_test.add_bluechi_node_config(node_good_cfg)
    bluechi_test.add_bluechi_node_config(node_with_long_loglevel_cfg)
    bluechi_test.add_bluechi_node_config(node_with_invalid_value_cfg)
    bluechi_test.add_bluechi_node_config(node_with_numbersonly_in_loglevel_cfg)

    bluechi_test.run(start_with_invalid_loglevel)
