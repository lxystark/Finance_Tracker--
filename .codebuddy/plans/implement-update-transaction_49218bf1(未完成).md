---
name: implement-update-transaction
overview: 实现修改交易记录功能，采用逐字段询问交互方式（回车跳过保留原值），与现有添加/删除功能的代码风格保持一致。
todos:
  - id: fix-update-func
    content: 修复 transaction.py 中 update_transaction 白名单含 tid 且缺少禁改守卫的问题
    status: pending
  - id: implement-edit-ui
    content: 在 main.py:106-112 的 else 分支中实现逐字段询问、kwargs 收集、调用更新并保存的完整逻辑
    status: pending
    dependencies:
      - fix-update-func
  - id: verify-lints
    content: 检查并修复新增代码可能引入的 linter 错误
    status: pending
    dependencies:
      - implement-edit-ui
---

## 产品概述

为 Finance_Tracker 项目的修改交易记录功能（choice == "3"）补全客户端交互逻辑。

## 核心功能

- 在 `main.py:106-112` 的 else 分支中，替换 `# TODO` 占位符，实现逐字段修改交互
- 依次询问 6 个可编辑字段（tid, type, amount, category, date, note），每个字段显示当前值，用户直接回车则保留原值，输入新内容则更新该字段
- 收集所有非空输入后调用已有的 `update_transaction(file, tid, **kwargs)` 执行更新
- 调用 `save_data(file)` 持久化修改结果
- 打印成功/无变更提示

### 交互流程示例

```
--- 修改交易记录 ---
请输入要修改的交易ID (输入 Q 取消，输入 S 查看所有交易记录): 1

待修改的交易记录：
{
  "tid": 1,
  "type": "支出",
  "amount": 50.0,
  "category": "餐饮",
  "date": "2024-01-15",
  "note": "午饭"
}
交易ID [1]: 
类型 [支出]: 
金额 [50.0]: 60.0
分类 [餐饮]: 
日期 [2024-01-15]: 2024-01-16
备注 [午饭]: 晚饭
已修改交易 #1
```

### 额外修复

- `update_transaction()` 白名单中包含 `"tid"`，需保留 tid 可编辑（用户确认 tid 允许修改）
- **tid 查重**：若用户修改了 tid，新 tid 不能与已有交易重复，需在收集 input 时做查重校验

## 技术栈

- Python 3.x 命令行应用
- 现有架构：DoublyLinkedList + Transaction 模型 + JSON 持久化

## 实现方案

采用**逐字段询问**策略，在显示当前交易记录后，对每个可编辑字段执行以下逻辑：

1. 用 f-string 显示字段名和当前值：`类型 [{current_value}]: `
2. 用户输入为空字符串 → 跳过（保留原值）
3. 用户有输入 → 对 tid/amount 字段分别做 `int()`/`float()` 类型转换后存入 kwargs 字典，其余字段直接存入字符串
4. **tid 查重**：若用户输入了新 tid，需调用 `check_tid_exists()` 验证新 tid 未被占用（排除自身）
5. 所有字段询问完毕后，若 kwargs 非空则调用 `update_transaction(file, tid, **kwargs)` 并 `save_data(file)`；若 kwargs 为空（用户全部回车）则提示"未做任何修改"

## 关键实现细节

- **文件修改范围**：
- `main.py:106-112`：替换 else 分支内的 TODO 为完整的逐字段询问 + 更新逻辑
- `models/transaction.py:92-99`：移除 update_transaction 中禁止 tid 修改的守卫逻辑（用户确认 tid 允许修改），保留白名单中的 `"tid"`
- **tid/amount 特殊处理**：tid 输入需要 `int()` 转换 + `check_tid_exists()` 查重；amount 需要 `float()` 转换；均需包裹 try/except 防止非法输入
- **代码风格一致**：复用删除功能的确认模式（先展示详情再操作）、复用添加功能的 input 模式
- **tid 变量作用域**：确保 tid 使用代码在 else 分支内，与现有删除功能保持一致的缩进结构

## 数据流

```
用户输入 tid → 存在性验证 → 显示当前记录 → 逐字段收集(回车跳过) → kwargs字典 → update_transaction() → save_data() → 提示成功
```