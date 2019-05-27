from unittest.mock import MagicMock, patch

import pytest

from UM.Settings.ContainerRegistry import ContainerRegistry
from cura.Settings.ExtruderManager import ExtruderManager
from cura.Settings.MachineManager import MachineManager


@pytest.fixture()
def global_stack():
    return MagicMock(name="Global Stack")

@pytest.fixture()
def container_registry() -> ContainerRegistry:
    return MagicMock(name = "ContainerRegistry")


@pytest.fixture()
def extruder_manager(application, container_registry) -> ExtruderManager:
    if ExtruderManager.getInstance() is not None:
        # Reset the data
        ExtruderManager._ExtruderManager__instance = None

    with patch("cura.CuraApplication.CuraApplication.getInstance", MagicMock(return_value=application)):
        with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", MagicMock(return_value=container_registry)):
            manager = ExtruderManager()
    return manager


@pytest.fixture()
def machine_manager(application, extruder_manager, container_registry, global_stack) -> MachineManager:
    application.getExtruderManager = MagicMock(return_value = extruder_manager)
    application.getGlobalContainerStack = MagicMock(return_value = global_stack)
    with patch("cura.Settings.CuraContainerRegistry.CuraContainerRegistry.getInstance", MagicMock(return_value=container_registry)):
        manager = MachineManager(application)

    return manager


def test_setActiveMachine(machine_manager):
    registry = MagicMock()

    mocked_global_stack = MagicMock()

    mocked_global_stack.getId = MagicMock(return_value = "test_machine")
    registry.findContainerStacks = MagicMock(return_value = [mocked_global_stack])
    with patch("cura.Settings.CuraContainerRegistry.CuraContainerRegistry.getInstance", MagicMock(return_value=registry)):
        with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", MagicMock(return_value=registry)):
            machine_manager.setActiveMachine("test_machine")

            # Although we mocked the application away, we still want to know if it was notified about the attempted change.
            machine_manager._application.setGlobalContainerStack.assert_called_with(mocked_global_stack)


def test_hasUserSettings(machine_manager, application):
    mocked_stack = application.getGlobalContainerStack()

    mocked_instance_container = MagicMock(name="UserSettingContainer")
    mocked_instance_container.getNumInstances = MagicMock(return_value = 12)
    mocked_stack.getTop = MagicMock(return_value = mocked_instance_container)

    assert machine_manager.numUserSettings == 12
    assert machine_manager.hasUserSettings
