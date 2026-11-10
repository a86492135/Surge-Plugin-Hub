# 安装指南

## 选择模块

| 应用 | 名称 | 要求 |
| --- | --- | --- |
| 高德地图 | Ads Bolck丨高德地图 | MITM、重写、脚本及已信任的 Surge CA |
| 微博 | Ads Bolck丨微博 | MITM、重写、脚本及已信任的 Surge CA |
| 飞常准业内版 | Ads Bolck丨飞常准业内版 | 域名规则；无需 MITM 或脚本 |
| 软件去广告合集 | Ads Bolck丨软件去广告合集 | MITM、重写、脚本；外部脚本需可下载 |

作者均为 `Belief`，分类为 `Belief’s Ad Block`。

## 通过 URL 安装

在 Surge 的模块管理中，通过 URL 添加对应地址并启用。也可保存 Raw 文件后导入；GitHub 的 blob 网页地址不能代替 Raw 地址。

**高德地图**

```text
https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-AMap.sgmodule
```

**微博**

```text
https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-Weibo.sgmodule
```

**飞常准业内版**

```text
https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-VariFlightPro.sgmodule
```

**软件去广告合集**

```text
https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-BlockAds.sgmodule
```

## 启用与更新

1. 停用处理同一 App 的重复模块，避免响应被多次处理。
2. 高德、微博及软件去广告合集按上表启用所需功能，并确认手机信任当前 Surge 证书；飞常准无需这一步。
3. 从后台关闭对应 App，再重新打开检查效果。
4. 仓库更新后，刷新 Surge 的远程模块及相关脚本，再重启 App。

无需为安装这些模块更改代理节点或监听端口。高德包含 jq 响应重写，其最低版本要求见 [Surge 官方说明](https://manual.nssurge.com/http/body-rewrite.html)。

## 验证与恢复

高德的开屏、扫街榜2026入口及双11横幅已在目标 iPhone 验证；底栏隐藏尚未实现。微博、飞常准业内版和软件去广告合集待实机验证，具体范围见各模块说明。

如出现功能异常，先停用对应模块，再重启 App 比较。飞常准的域名规则为全局匹配，也可能影响其他 App 对同一域名的访问。
