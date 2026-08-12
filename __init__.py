"""Source-tree entry point for direct Hermes plugin installs.

The distributable Python package lives in ``hermes_harbor``.
Keeping this thin wrapper at the repository root also makes
``hermes plugins install smfworks/hermes-plugin-harbor`` work.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hermes_harbor import register
elif __package__:
    from .hermes_harbor import register
else:
    from hermes_harbor import register

__all__ = ["register"]
