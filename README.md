<div align="center">

![Surge插件中心 · Belief](assets/banner.svg)

# Surge插件中心

**更少推广，更专注的日常使用。**

![Maintainer](https://img.shields.io/badge/Maintainer-Belief-61DACB?style=flat-square&labelColor=111827)
![Platform](https://img.shields.io/badge/Platform-Surge-93C5FD?style=flat-square&labelColor=111827)
![Status](https://img.shields.io/badge/Status-待实机验证-FBBF24?style=flat-square&labelColor=111827)

[浏览模块](#模块目录) · [安装指南](docs/INSTALL.md) · [更新记录](CHANGELOG.md) · [来源说明](THIRD_PARTY_NOTICES.md)

</div>

---

## 模块目录

<table>
<tr><td>

### 🗺️ Ads Bolck丨高德地图

整合推广内容清理规则与首页运营图标补丁，保持单文件导入。

**包含：** 开屏、首页推荐、搜索推荐、打车推广、地点推荐及我的页精简规则。

**版本：** `0.2.0`　 **更新：** `2026-11-04`　 **状态：** 实验版

[下载模块](https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-AMap.sgmodule) · [查看详情](docs/AMAP.md) · [安装步骤](docs/INSTALL.md)

</td></tr>
</table>

### 🐦 Ads Bolck丨微博

开屏、信息流、热搜、评论区及个人页推广净化。运行脚本固定到具体上游版本，更新随 PR 审核。

**分类：** `Belief’s Ad Block`　 **作者：** `Belief`　 **状态：** 待实机验证

[下载微博模块](https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-Weibo.sgmodule) · [模块说明](docs/WEIBO.md)

> **验证状态**：模块通过 Surge 配置语法检查；新增图标补丁通过 16 个模拟数据用例。尚未完成目标手机上的去广告效果验证。“扫街榜 2026”已反馈仍存在，正在定位；不包含底栏只留“首页”和“我的”的功能。

## 开始使用

1. 打开模块文件，点击 **Raw / 原始文件** 获取完整模块。
2. 在 Surge 的模块管理中导入文件，或在公开仓库中复制 Raw 链接，通过 URL 安装。
3. 仅启用这一份高德净化模块，关闭其他重复模块。
4. 确认 MITM、重写与脚本已开启，且手机信任当前 Surge 证书。
5. 从后台彻底退出高德，再打开检查效果。

遇到问题时先停用本模块，重启高德确认是否恢复。请勿为了测试直接卸载高德，以免丢失离线地图与本地数据。

## 自动同步

每天北京时间 **10:17** 检查一次（GitHub 排队可能延迟），也可在 Actions 中手动运行 **Sync upstream rules**。

来源优先级：指定目录的 Surge 模块 → 可莉 Loon 插件转译 → 已审阅的备用上游。当前可莉站点返回 403，因此微博暂用 fmz200 的固定版本；每日继续检查优先源。

有变化时自动开 PR，**不会自动合并，也不会在合并前替换已发布模块**。Belief 名称、分类、简短描述与本地补丁由配置层保留。无法可靠转换的 Loon 语法会记录为待审核，不静默丢弃。

[同步机制与转译边界](docs/SYNC.md) · [查看同步工作流](../../actions/workflows/sync-upstream.yml)

## 维护约定

- **一个模块，一个入口**：提供可直接导入的 `.sgmodule` 文件。
- **明确验证状态**：区分静态检查、模拟数据测试与实机验证。
- **记录每次改动**：变更范围与已知限制见模块说明和更新记录。
- **只分享规则**：仓库不包含账号凭据、证书私钥、代理节点或个人抓包记录。

## 目录结构

```text
Surge-Plugin-Hub/
├── modules/                 Surge 模块
├── assets/                  仓库视觉素材
├── docs/                    安装与模块说明
├── scripts/                 规则静态检查
├── CHANGELOG.md             更新记录
├── THIRD_PARTY_NOTICES.md    第三方来源与署名
└── LICENSE                  授权文本
```

## 反馈与贡献

请使用仓库的反馈模板说明 App 版本、Surge 版本、具体入口和复现步骤。截图请遮挡位置、账号等个人信息；公开 Issue 中不要上传原始 HAR。

新增模块或规则前，请阅读 [贡献说明](CONTRIBUTING.md)。本仓库每天检查上游，只创建或更新同步 PR；经审核合并后才更新公开模块。手机端仍需刷新远程模块。

---

<div align="center">

**Belief** · 用清楚的规则，留住需要的功能。

</div>
