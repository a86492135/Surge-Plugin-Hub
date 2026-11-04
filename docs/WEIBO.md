# Ads Bolck丨微博

- 分类：`Belief’s Ad Block`
- 作者：`Belief`
- 描述：微博去广告
- 文件：`modules/Belief-Weibo.sgmodule`
- 状态：语法检查通过，待目标手机验证。

## 范围

包含开屏、信息流、发现页、热搜、评论、转发区、个人页等广告和推广清理。以官方微博客户端为主要测试目标；轻享版是否适配需另行验证。不要同时启用多套微博净化模块。

在已审阅的基础规则上排除皮肤及会员图标修改、非微博域名规则，并保留 SDK 响应清理脚本的可达性。每条脚本使用唯一标签，避免重名覆盖。

## 上游

优先检查 Repcz/Tool 的 Surge/Module/Kelee 目录，再尝试用户提供的官方 Loon 插件直链。当前目录没有普通微博模块，Loon 站点返回 403，暂用 fmz200/wool_scripts 的 Surge 原生规则。

外部运行脚本引用固定的 Git 提交，不能绕过同步 PR 独立追随上游 main。来源、提交与摘要见 upstream.lock.json；优先来源的读取结果见 upstream-review.json。

本模块的第三方基础规则按 GPL-3.0 发布，授权文本见 LICENSES/Weibo-GPL-3.0.txt；Belief 是本仓库的维护者。
