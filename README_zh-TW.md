[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/tsunglung/sampo_exohome?style=for-the-badge)

[English](README.md) | [繁體中文](README_zh-TW.md)

# Sampo Home Plus

Home Assistant 的 Sampo Home Plus [Android](https://play.google.com/store/apps/details?id=tw.com.sampo.sampohomeplus&hl=zh_TW&pli=1) [iOS](https://apps.apple.com/tw/app/sampo-home-plus/id1491290905) 整合套件
## 注意

1. 本整合套件僅支援 Sampo Home Plus 模組最新版本，請更新 Sampo Home Plus 模組的韌體到最新版本。
2. 這套件全新改寫，歡迎回報。目前已支援空調，洗衣機，冰箱，除溼機，全熱交換機和重量感知板。
3. 由於 Sampo Home Plus 家電有很多型號，每個型號功能都不一樣，如果遇到問題，歡迎回報問題給我修復問題。

# 安裝

你可以用 [HACS](https://hacs.xyz/) 來安裝這個整合。 步驟如下 custom repo: HACS > Integrations > 3 dots (upper top corner) > Custom repositories > URL: `tsunglung/sampo_exohome` > Category: Integration

# 手動安裝

手動複製 `sampo_exohome` 資料夾到你的 config 資料夾的  `custom_components` 目錄下。

然後重新啟動 Home Assistant.

# 設定

**請使用 Home Assistant 整合設定**

1. 從 GUI. 設定 > 整合 > 新增 整合 > Sampo Home Plus
   1. 如果 `Sampo Home Plus` 沒有出現在清單裡，請 重新整理 (REFRESH) 網頁。
   2. 如果 `Sampo Home Plus` 還是沒有出現在清單裡，請清除瀏覽器的快取 (Cache)。
2. 輸入登入資訊 ([Panasonic Cloud](https://www.sampo.com.tw/) 的電子郵件及密碼)
3. 開始使用。

打賞

|  LINE Pay | LINE Bank | JKao Pay |
| :------------: | :------------: | :------------: |
| <img src="https://github.com/tsunglung/TwANWS/blob/master/linepay.jpg" alt="Line Pay" height="200" width="200">  | <img src="https://github.com/tsunglung/TwANWS/blob/master/linebank.jpg" alt="Line Bank" height="200" width="200">  | <img src="https://github.com/tsunglung/TwANWS/blob/master/jkopay.jpg" alt="JKo Pay" height="200" width="200">  |