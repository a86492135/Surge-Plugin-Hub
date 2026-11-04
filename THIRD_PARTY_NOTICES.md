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

早期另曾比对 [ddgksf2013/Rewrite 的高德规则](https://github.com/ddgksf2013/Rewrite/blob/master/AdBlock/AmapAds.conf)。其混淆脚本未打包进本仓库，当时的高德模块未引用远程第三方 JavaScript；本次新增微博模块的固定脚本依赖见下节。

## 微博模块

基础规则来自 fmz200/wool_scripts 的 Surge/module/weibo.module，作者标注为奶思 / fmz200，部分基础工作引用 zmqcherish。运行的 weibo_ads.js、weibo_main.js 使用具体提交的固定链接，完整版本记录在 upstream.lock.json 中。适用 GPL-3.0 授权，文本见 LICENSES/Weibo-GPL-3.0.txt；根目录 MIT 授权不重新授权这一组件。

本次维护移除皮肤与会员图标功能、无关域名及冲突的 SDK 拦截，并用 Belief 自编的开屏清理脚本替换第三个外部脚本。高德和微博的元数据作者 Belief 均表示本仓库维护者，第三方基础规则不是重新标记为独立原创。

优先来源按用户指定设置为 Repcz/Tool 的 Surge/Module/Kelee 目录，其次为官方 Loon 插件转译。可莉微博 Loon 站点当前返回 403，尚未把不可读内容宣称为已转译。

## 首页扫街榜定向补丁的字段参考

- 参考：[ifls4816/ios-qx-script，固定版本 Amap.js](https://github.com/ifls4816/ios-qx-script/blob/7d55231219a471d9cee09383b92c7a46629b4933/loon/scripts/Amap.js#L126)。该实现说明了 UserAssetsVirtualCard.newIcon 和工具列表与首页右上角图标的关系，以及空列表可能沿用缓存的情况。
- 本仓库独立编写 `scripts/amap-home.js`，仅实现相关字段清理、异常原样通过及计数日志，没有引入或执行完整第三方脚本。该参考不表示当前高德版本已实机验证。

## 飞常准业内版

- 原始域名规则由仓库使用者在本次维护中提供，共 14 条，域名与顺序原样保留。
- 本仓库补全 Belief 名称、分类、简短描述、日期和安装说明；没有引入第三方脚本或外部同步源。
- 手动来源：`rules/variflight-pro.list`；发布模块：`modules/Belief-VariFlightPro.sgmodule`。
