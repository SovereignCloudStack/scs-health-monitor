# Testing OpenStack using StackMon

## Overview
This documentation outlines the process of testing StackMon, a tool designed for testing OpenStack clouds using Ansible Playbooks. It covers the steps from setting up the environment to encountering and resolving issues during testing.

## Setup

1) Cloning the Repository: Begin by cloning the StackMon repository to your local machine.

2) Creating Virtual Environment: Create a virtual environment using .venv to isolate dependencies.

3) Installing Requirements: Install the required dependencies as specified in the README.md file.

## Initial Issues Encountered

Python Version Compatibility: Initially, there were compatibility issues with Python 3.8, specifically with importlib.resources. Resolution: Upgraded to Python 3.10 to resolve the compatibility issue.

Got an error: 'StackMonConfig' object has no attribute 'model'

Description: The testing process encountered an error related to the StackMonConfig object's attribute 'model'.

``` bash
(erik) erik@LAPTOP-RN6QAE6M:~/git/4) dNation/StackMon$ StackMon --config config.yaml --inventory .\etc\inventory_quickstart\hosts apimon provision --debug -v
initialize_app ['apimon', 'provision']
prepare_to_run_command ApiMonProvision
Provisioning ApiMon
'StackMonConfig' object has no attribute 'model'
Traceback (most recent call last):
  File "/home/erik/.local/lib/python3.10/site-packages/cliff/app.py", line 410, in run_subcommand
    result = cmd.run(parsed_args)
  File "/home/erik/.local/lib/python3.10/site-packages/cliff/command.py", line 181, in run
    return_code = self.take_action(parsed_args) or 0
  File "/mnt/c/Users/koste/Git/4) dNation/StackMon/StackMon/cli/apimon.py", line 27, in take_action
    manager = ApiMonManager(self.app.config)
  File "/mnt/c/Users/koste/Git/4) dNation/StackMon/StackMon/plugin/apimon.py", line 54, in __init__
    self.process_config()
  File "/mnt/c/Users/koste/Git/4) dNation/StackMon/StackMon/plugin/apimon.py", line 63, in process_config
    for matrix_entry in self.config.model.matrix:
AttributeError: 'StackMonConfig' object has no attribute 'model'
clean_up ApiMonProvision
got an error: 'StackMonConfig' object has no attribute 'model'
```

Resolution: (To be filled once resolved)


## Conclusion

This documentation provides insights into the testing process of StackMon from a user perspective. It highlights the encountered issues and their resolutions, up to the current progress made in testing.

## References
[StackMon repository](https://github.com/stackmon/cloudmon)

[StackMon architecture](https://stackmon.org/)

[StackMon conference presentation](https://www.youtube.com/watch?v=otIH7kn-GAU)