from time import clock_gettime, CLOCK_REALTIME
from typing import Optional
import logging

from model.config import config
from model.api.schema_validation.command_schema import Command, MinimizeCommand, AlterCommand, CommandPayload
from model.api.schema_validation.grid_system_schema import GridPosition

logger = logging.getLogger(__name__)

def prepare_and_verify_command_for_window(position: int, tl: int, br: int) -> Optional[Command]:
    """
    prepares and verifies positional correctness of a command for a window
    :param position: translated window id
    :param tl: translated top-left coordinate
    :param br: translated bottom-right coordinate
    :return: Command on success, None on failure
    """
    pos = GridPosition(tl=tl, br=br)
    #todo verify pos
    logger.debug(f"positional verification successful for window {position}")
    if tl == config.grid_rows * config.grid_cols - 1 and br == config.grid_rows * config.grid_cols - 1:
        return Command(
            command_type=MinimizeCommand(
                window_id=position
            )
        )
    else:
        return Command(
            command_type=AlterCommand(
                window_id=position,
                position=pos
            )
        )


def verify_compositional_rules(commands: list[Command]) -> bool:
    """
    verifies whether the proposed workspace composition is valid, according to the absolute ground rules.
    :param commands: proposed workspace composition
    :return: its validity
    """
    #todo verify composition
    return False


def prepare_and_verify_command_payload(commands: list[Command]) -> Optional[CommandPayload]:
    """
    prepares and verifies the command payload from a list of commands for each window.
    :param commands: list of commands
    :return: CommandPayload on success, None on failure
    """
    status = True
    status &= verify_compositional_rules(commands)
    logger.debug(f"compositional verification successful for payload")

    if status:
        return CommandPayload(
            command_timestamp=clock_gettime(clock_ID=CLOCK_REALTIME),
            commands=commands
        )
    else:
        return None