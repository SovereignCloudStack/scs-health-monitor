Feature: Create disk from image in OpenStack

Scenario: Create a disk from an image
    Given I am connected to OpenStack
    When I create a volume from image "image_name_or_id" with size 10 GB and name "new_volume_from_image"
    Then the volume should be successfully created