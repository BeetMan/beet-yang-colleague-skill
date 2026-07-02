# 比特羊 Skill

一个用于 Codex 的个人风格 Skill，基于 Beet Yang / 比特羊的公开频道语料和用户提供的资料整理而成。

这个仓库只包含可公开发布的 Skill 文件和辅助脚本，不包含原始 Telegram 导出、完整爬取语料、截图或媒体文件。

## 内容

- `colleagues/beet-yang/SKILL.md`: Codex Skill 入口
- `colleagues/beet-yang/persona.md`: 表达风格、判断方式和人设规则
- `colleagues/beet-yang/work.md`: 产品观察、导购、短评、工具发布等工作方式
- `colleagues/beet-yang/meta.json`: 版本、样本范围和资料来源摘要
- `tools/crawl_beet_select.py`: `beet.select` 的可恢复爬取脚本

## 安装到 Codex

把 Skill 目录复制到 Codex 用户技能目录：

```powershell
Copy-Item -Recurse -Force `
  "colleagues\beet-yang" `
  "$env:USERPROFILE\.codex\skills\colleague-beet-yang"
```

然后重启 Codex。

使用时可以说：

```text
使用 colleague-beet-yang skill
```

或者更自然地说：

```text
用 Beet Yang 的风格评价一下这个产品。
```

## 数据边界

当前公开版本的 `meta.json` 记录了样本规模和时间范围，但不会公开原始语料。

原因：

- 原始 Telegram 导出包含完整历史消息、链接、时间戳和上下文。
- 公开 Skill 只需要保留蒸馏后的风格和工作方式。
- 原始语料继续由频道/网站所有者自行保管。

## 版本

Skill 版本写在 `colleagues/beet-yang/meta.json`。

当前公开版本基于：

- Telegram Desktop 导出的 11027 条消息
- 时间范围：2020-07-04 到 2026-07-02
- `beet.select` 的公开分页样本作为补充

## 许可

见 `LICENSE.md`。

- `tools/` 下的代码使用 MIT License。
- `colleagues/` 下的 Skill / profile 内容使用 CC BY-NC 4.0。
