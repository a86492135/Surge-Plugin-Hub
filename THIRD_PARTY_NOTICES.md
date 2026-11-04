# 第三方来源与署名

本仓库的高德模块是在第三方规则快照上合并补丁并调整展示元数据得到的维护版本。`#!author=Belief` 表示本仓库的维护者，不表示全部底层规则均为独立原创。

## 基础规则

- 原模块作者标注：可莉 🅥。
- 收录仓库：Repcz/Tool，分支 `X`。
- 文件：[Amap_remove_ads.sgmodule](https://github.com/Repcz/Tool/blob/X/Surge/Module/Kelee/Amap_remove_ads.sgmodule)。
- 原模块声明来源：[kelee.one](https://kelee.one/Tool/Loon/Lpx/Amap_remove_ads.lpx)。
- 获取的文件标注更新：2026-10-20 12:06:08；获取日期：2026-11-04。
- 收录仓库的 [MIT 授权](https://github.com/Repcz/Tool/blob/X/LICENSE) 已在本仓库 LICENSE 中保留相关版权声明。第三方作者或原站的其他声明仍应按其原文遵守。

## 本次维护改动

- 合并一条首页图标补丁，针对 `/updatable/1` 与 `/updatable/26`，处理 `mainIcon` / `mainBubble`。
- 图标补丁增加结构检查和无效数据保留处理。
- 合并、去重 MITM 域名。
- 调整模块名称、维护者与日期，并新增本仓库文档和静态检查。

另曾比对 [ddgksf2013/Rewrite 的高德规则](https://github.com/ddgksf2013/Rewrite/blob/master/AdBlock/AmapAds.conf)。其混淆脚本未打包进本仓库，当前模块不引用远程第三方 JavaScript。
