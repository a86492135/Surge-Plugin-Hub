<div align="center">

<img src="assets/banner.svg" alt="Surge插件中心 · Belief" width="100%" />

**Belief 维护的 Surge 去广告模块**

[![Checks](https://github.com/a86492135/Surge-Plugin-Hub/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/a86492135/Surge-Plugin-Hub/actions/workflows/validate.yml)
![Surge](https://img.shields.io/badge/Surge-iOS%20%2F%20macOS-61DACB?style=flat-square&labelColor=111827)
![Belief](https://img.shields.io/badge/Maintained%20by-Belief-93C5FD?style=flat-square&labelColor=111827)

[模块目录](#模块目录) · [安装指南](docs/INSTALL.md) · [更新记录](CHANGELOG.md) · [问题反馈](https://github.com/a86492135/Surge-Plugin-Hub/issues/new/choose)

</div>

## 模块目录

<!-- MODULES:START -->
| 模块 | 版本 / 更新 | 维护方式 | 验证状态 | 获取 |
| --- | --- | --- | --- | --- |
| **高德地图** | `0.3.4`<br>2026-11-05 | 上游检查 + PR | 部分实机通过 | [Raw 模块](https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-AMap.sgmodule) · [说明](docs/AMAP.md) |
| **微博** | `0.1.0`<br>2026-11-04 | 上游检查 + PR | 待实机验证 | [Raw 模块](https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-Weibo.sgmodule) · [说明](docs/WEIBO.md) |
| **飞常准业内版** | `0.1.0`<br>2026-11-05 | 手动维护 | 待实机验证 | [Raw 模块](https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-VariFlightPro.sgmodule) · [说明](docs/VARIFLIGHT.md) |
<!-- MODULES:END -->

统一分类：`Belief’s Ad Block`。点击 **Raw 模块** 获取安装地址，点击 **说明** 查看作用范围与验证记录。

| 🗺️ 地图 | 💬 社交 | ✈️ 出行 |
| --- | --- | --- |
| **高德地图**<br>开屏、首页、搜索等推广净化；保留首页图标与横幅补丁。 | **微博**<br>开屏、信息流、热搜、评论与个人页推广净化规则。 | **飞常准业内版**<br>用户提供的 14 条域名拦截规则；无需解密证书。 |

高德已验证的范围为开屏广告、扫街榜2026入口及双11横幅；**隐藏“探索／长按说话／打车”底栏尚未实现**。微博和飞常准仍待实机验证。

## 快速安装

1. 复制上表对应的 **Raw 模块** 链接。
2. 在 Surge 的模块管理中，通过 URL 添加并启用。
3. 根据[安装指南](docs/INSTALL.md)确认所需功能，再重启对应 App 检查效果。

高德、微博需要开启相应的 MITM、重写与脚本功能；飞常准业内版只含域名规则，不需要 MITM 或脚本。

## 更新方式

**高德 / 微博**：每天北京时间 **10:17** 检查上游，有变化时自动创建或更新 PR，审核合并后发布。GitHub 定时任务可能延迟。

**飞常准业内版**：按用户提供的规则手动维护，日常同步只重建与检查本地规则，不接入外部上游。

公开模块保持固定地址；更新后在 Surge 中刷新远程模块及相关脚本。模块目录由统一配置生成，随同步 PR 更新。

[同步机制](docs/SYNC.md) · [同步工作流](https://github.com/a86492135/Surge-Plugin-Hub/actions/workflows/sync-upstream.yml)

## 仓库导航

| 内容 | 位置 |
| --- | --- |
| 可直接安装的模块 | [modules/](modules/) |
| 安装、范围与验证记录 | [docs/](docs/) |
| 手动维护的域名规则 | [rules/](rules/) |
| 高德本地补丁 | [overrides/](overrides/) |
| 名称、分类、来源与验证状态 | [config/modules.json](config/modules.json) |
| 模块版本与文件摘要 | [manifest.json](manifest.json) · [校验和](checksums.sha256) |

<details>
<summary>维护与贡献</summary>

构建与检查位于 [scripts/](scripts/)，回归用例位于 [tests/](tests/)。提交规则前请阅读[贡献说明](CONTRIBUTING.md)。

反馈时请注明模块、App / Surge 版本、入口与复现步骤。公开反馈中请遮挡账号和位置，不上传个人配置、证书私钥或原始抓包。

</details>

---

**Belief** · [来源与署名](THIRD_PARTY_NOTICES.md) · [仓库许可](LICENSE) · [微博组件许可](LICENSES/Weibo-GPL-3.0.txt)
