from typing import Literal, TypeAlias

EnableKeys: TypeAlias = Literal["html", "markdown"]
ConfigEnable: TypeAlias = dict[EnableKeys, bool]

ConfigKeys: TypeAlias = Literal["enabled"]
ConfigValues: TypeAlias = ConfigEnable

Config = dict[ConfigKeys, ConfigValues]
