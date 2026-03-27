from __future__ import annotations

INVERTER_TYPE = 80
BMS_TYPE = 112

REAL_INFO_COMMAND = "wifilocalMonitor:get dev real infor"
BASIC_INFO_COMMAND = "wifilocalMonitor:get dev basice infor"
SET_INFO_COMMAND = "wifilocalMonitor:get dev set infor"

POLL_COMMANDS: dict[str, str] = {
	"real": REAL_INFO_COMMAND,
	"basic": BASIC_INFO_COMMAND,
	"set": SET_INFO_COMMAND,
}
