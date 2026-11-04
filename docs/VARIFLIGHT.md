# Ads Bolck丨飞常准业内版

| 项目 | 内容 |
| --- | --- |
| 模块 | `modules/Belief-VariFlightPro.sgmodule` |
| 版本 / 日期 | 0.1.0 / 2026-11-05 |
| 作者 / 分类 | Belief / Belief’s Ad Block |
| 规则来源 | 用户提供的 14 条域名规则 |
| 维护方式 | 手动维护，不接入外部同步源 |
| 验证 | Surge 配置解析通过，待实机验证 |

[获取 Raw 模块](https://raw.githubusercontent.com/a86492135/Surge-Plugin-Hub/main/modules/Belief-VariFlightPro.sgmodule) · [安装指南](INSTALL.md)

## 使用

在 Surge 模块管理中通过上面的 Raw 地址添加、启用，再重新打开飞常准业内版。模块仅包含 `DOMAIN-SUFFIX` 拒绝规则，**无需 MITM、解密证书或脚本**。

域名和顺序均保留用户原稿，完整规则见 [rules/variflight-pro.list](../rules/variflight-pro.list)。没有新增抓包、账号操作或功能解锁。

这些规则按域名全局生效，其他 App 访问同一域名也会被拦截；如有功能受影响，可单独停用此模块比较。

## 维护

修改本地规则列表后由构建程序生成模块、校验和与首页目录。每日上游检查会保留这份本地来源，不会用其他插件替换。

当前只确认规则文件能被 Surge 解析；未完成目标手机上的广告消失与正常航班功能验证。
