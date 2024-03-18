# Feature Testing and Next Steps Recommendations

## Overview

This document details feature testing practices and provides action recommendations to enhance our development workflow.

#### Current Test Scenario Structure

- **Creating Resources**:
  - Create routers: `behave ./features/openstack_create_router.feature`
  - Create networks: `behave ./features/openstack_create_network.feature`
  - Create subnets: `behave ./features/openstack_create_subnet.feature`

- **Deleting Resources**:
  - Delete subnets: `behave ./features/openstack_delete_subnet.feature`
  - Delete networks: `behave ./features/openstack_delete_network.feature`
  - Delete routers: `behave ./features/openstack_delete_router.feature`

#### Behave Test Execution Order and Structure

To ensure the Behave tests execute in the correct order, reflecting the dependency structure of the OpenStack resources, the feature files in the `./features/` directory need to be structured accordingly. Behave executes feature files in alphabetical order, which is crucial for managing resource dependencies.

2. **Behave**: Behave executes feature files in alphabetical order within the `./features/` directory. This execution order is crucial for managing the creation and deletion of dependent resources.

3. **Execution Order of features**: Resources should be created and deleted to maintain the logical structure and dependencies:

   - **Creation Order**:
     1. Routers (VPC)
     2. Networks
     3. Subnets
   - **Deletion Order**:
     1. Subnets
     2. Networks
     3. Routers (VPC)

#### Recommended Actions for features

To enhance the organization and execution of the Behave tests, the following actions are recommended for consideration:

1. **Feature File Restructuring**: It's advised to consider renaming the feature files in the `./features/` directory to align with their execution order. A numbering prefix can help dictate the sequence and ensure dependencies are respected. For instance:

   - `01_create_router.feature`
   - `02_create_network.feature`
   - `03_create_subnet.feature`
   - `04_delete_subnet.feature`
   - `05_delete_network.feature`
   - `06_delete_router.feature`
     
#### Recommended Actions for steps.py

**Modular Design vs Script Organization:**

In our pursuit of enhancing the maintainability and readability of our Behave step definitions, we are presented with two primary organizational strategies: adopting a modular design by splitting our step definitions across multiple scripts or refining the structure of our existing single script.

## Conclusion

This document outlines our testing approach, identifying issues, solutions, and progress in our feature testing. 
It highlights the encountered issues and recommended resolutions.
It serves as a guide for ongoing and future testing efforts, ensuring quality and efficiency in our development process.
