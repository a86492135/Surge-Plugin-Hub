# 安装指南

## 获取模块

模块：[Belief-AMap.sgmodule](../modules/Belief-AMap.sgmodule)。Surge 内显示名称为“Belief的模块”，维护作者为 Belief。

在 Surge 的模块管理中通过 URL 添加以下地址：

```text
https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-AMap.sgmodule
```

也可将 Raw 文件保存到“文件”App，再使用 Surge 的模块导入功能。不要把 GitHub 的 blob 网页链接当成模块地址。

## 启用

1. 停用其他高德净化模块和独立图标补丁，避免重复处理。
2. 确认 MITM 与重写已开启，手机信任当前配置使用的 Surge CA。
3. 保留现有代理与监听端口，无需为本模块修改。
4. 从后台彻底退出高德，再重新打开。

模块包含 jq 响应重写，要求 Surge iOS 5.14.0+ / Mac 5.9.0+，以 [官方说明](https://manual.nssurge.com/http/body-rewrite.html)为准。

## 检查与恢复

分别检查冷启动、首页、我的、搜索、路线规划与导航预览。补丁是否能去除“扫街榜 2026”仍待实机验证，单次没有广告不代表全部有效。

如出现功能异常，先停用本模块，再从后台退出高德重新打开。不建议直接卸载高德或清空离线地图。
