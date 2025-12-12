# Felicity Inverter (Home Assistant)

Custom integration for Felicity inverter devices that expose the local TCP API on **port 53970**.

This integration was created as an inverter-focused analogue of the battery integration, and reads these commands:

- `wifilocalMonitor:get dev real infor`
- `wifilocalMonitor:get dev basice infor`
- `wifilocalMonitor:get dev set infor`

## Install (HACS)

1. In HACS → **Integrations** → **⋮** → **Custom repositories**
2. Add your GitHub repository URL and select category **Integration**
3. Install and restart Home Assistant
4. Settings → **Devices & services** → **Add integration** → **Felicity Inverter**

## Install (manual)

Copy `custom_components/felicity_inverter` into:

```
config/custom_components/felicity_inverter
```

Restart Home Assistant.

## Configuration

Add via UI (Config Flow):

- **Name** (any)
- **Host** (IP of inverter WiFi module)
- **Port** (default: 53970)

## Sensors

The integration exposes a small, practical set of sensors from `dev real infor`:

- Battery SOC / Battery Voltage
- Load Percent
- Power Flow
- Bus Voltage
- AC Input Voltage/Current/Power
- AC Output Voltage/Current/Power
- Temperatures (first 4 values from `Temp[0]`)

And diagnostic sensors:

- Work Mode (`workM`)
- Warning Code (`warn`)
- Fault Code (`fault`)
- Firmware Version (`_basic.version`)

### Scaling notes

Based on observed payloads, some values appear scaled:

- `Batsoc[0][0]` → % = value / 100
- `Batt[0][0]` → V = value / 1000
- `lPerc` → % = value / 10
- `busVp` → V = value / 10
- `ACin/ACout` voltage/current/power → value / 10
- `Temp[0][n]` → °C = value / 10

If your device uses different scaling, adjust conversions in `sensor.py`.

## Support / Debug

Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.felicity_inverter: debug
```

## Disclaimer

This is an unofficial community integration.
