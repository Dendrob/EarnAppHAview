# EarnAppHAView for Home Assistant

EarnAppHAView is a custom Home Assistant integration that displays account,
earnings, device, transaction, and referral data from EarnApp. It uses
[pyEarnapp](https://github.com/fazalfarhan01/EarnApp-API) and refreshes data
every 30 minutes.

> [!WARNING]
> This integration uses EarnApp dashboard endpoints, which may change without
> notice. Your OAuth refresh token grants access to your account. Never share
> it or commit it to a public repository.

## Features

- Configurable through Home Assistant's integration setup flow.
- Periodic updates every 30 minutes.
- Account, earnings, device, transaction, and referral sensors.
- Detailed resource data available as sensor attributes.

## Installation

### HACS

1. In HACS, open **Integrations**.
2. Add `https://github.com/Dendrob/EarnAppHAview` as a custom repository with
   the **Integration** category.
3. Install **EarnAppHAView**, then restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration**.
5. Search for **EarnAppHAView** and enter your `oauth-refresh-token` value.

## Get your OAuth refresh token

1. Sign in to the [EarnApp dashboard](https://earnapp.com/dashboard/) with your
   Google account.
2. Open your browser's developer tools (`Ctrl+Shift+I` on Windows/Linux or
   `Cmd+Option+I` on macOS).
3. Select the **Network** tab and reload the page.
4. Search for `oauth-refresh-token` and select a matching request.
5. Open its **Cookies** tab and copy the value of `oauth-refresh-token`—not the
   cookie name.
6. Paste the value into the EarnAppHAView integration setup form.

## Sensors and data

The integration creates sensors for the following data. Detailed resource
responses are available as sensor attributes.

| Category | Data |
| --- | --- |
| Account and earnings | Account details, balance, total earnings, referral bonuses, and earnings multiplier |
| Devices | Total devices, Windows devices, Linux devices, other devices, banned devices, and bandwidth usage |
| Transactions | Total transactions, pending payments, and paid transactions |
| Referrals | Referral count, referral earnings, and total referral earnings |

Data is retrieved using the `pyEarnapp` methods `get_user_data`,
`get_earning_info`, `get_devices_info`, `get_transaction_info`, and
`get_referral_info`.

## Dashboard

The [`dashboard/earnapp.yaml`](dashboard/earnapp.yaml) file provides a
Lovelace dashboard with account, earnings, device, transaction, and referral
data, including the detailed API attributes.

Create a YAML dashboard in Home Assistant and copy the file contents into it.
If Home Assistant assigned different entity IDs, update the dashboard's
`sensor.earnapp_*` references to match the IDs shown under
**Settings > Devices & services > Entities**.

## Limitations

The integration depends on EarnApp dashboard endpoints and the `pyEarnapp`
library. These may change without notice.
