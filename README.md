[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/tsunglung/sampo_exohome?style=for-the-badge)


[繁體中文](README_zh-TW.md) | [English](README.md)

# Sampo Home Plus

Home Assistant integration for Sampo Home Plus [Android](https://play.google.com/store/apps/details?id=tw.com.sampo.sampohomeplus&hl=zh_TW&pli=1) [iOS](https://apps.apple.com/tw/app/sampo-home-plus/id1491290905).

This integration allows you to control your Sampo Home Plus appliances.

## Note

1. This integration only support the latest version of Sampo Home Plus module, please use the latest version of IoT module.
2. The code was refacotred, currently support Climate, Air Purifier.
3. The Sampo Home Plus appliances have a lot of models, so some appliances may support well. Welcome to report the issue to me to fix it.

# Installation

You can install component with [HACS](https://hacs.xyz/) custom repo: HACS > Integrations > 3 dots (upper top corner) > Custom repositories > URL: `tsunglung/sampo_exohome` > Category: Integration

Then restart Home Assistant.

### Manually Installation

Copy `sampo_exohome` folder of custom_components in this repository to `custom_components` folder in your config folder.

# Configuration

**Please use the config flow of Home Assistant**

1. With GUI. Configuration > Integration > Add Integration > `Sampo Home Plus`
   1. If the integration didn't show up in the list please REFRESH the page
   2. If the integration is still not in the list, you need to clear the browser cache.
2. Enter the Login info (email and password of [Sampo Home Plus](https://www.sampo.com.tw/))
3. Enjoy

Buy Me A Coffee

|  LINE Pay | LINE Bank | JKao Pay |
| :------------: | :------------: | :------------: |
| <img src="https://github.com/tsunglung/TwANWS/blob/master/linepay.jpg" alt="Line Pay" height="200" width="200">  | <img src="https://github.com/tsunglung/TwANWS/blob/master/linebank.jpg" alt="Line Bank" height="200" width="200">  | <img src="https://github.com/tsunglung/TwANWS/blob/master/jkopay.jpg" alt="JKo Pay" height="200" width="200">  |

