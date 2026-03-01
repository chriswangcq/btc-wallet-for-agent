# 🤖💰 BTC Wallet for AI Agents

> **首个专为 AI Agent 设计的比特币钱包**
> 
> 让 AI 拥有真正的经济自主权 —— 无需人类干预，自主收发比特币

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Bitcoin](https://img.shields.io/badge/bitcoin-testnet%2Fmainnet-orange.svg)](https://bitcoin.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ 一句话介绍

```
AI Agent + Bitcoin = 真正自治的智能经济实体
```

这个钱包让 AI Agent 能够：
- 🏦 **自主管理** 比特币资产
- 💸 **自动收发** 支付和收款
- 🔗 **无需信任** 第三方或人类中介
- ⚡ **实时结算** 全球范围内 10 分钟到账

---

## 🚀 5 分钟快速开始

### 安装

```bash
git clone https://github.com/chriswangcq/btc-wallet-for-agent.git
cd btc-wallet-for-agent
pip install -r requirements.txt
```

### AI Agent 使用示例

```python
from wallet_core import Wallet

# AI Agent 创建自己的钱包
wallet = Wallet(testnet=True)
wallet.create_new()

print(f"我的地址: {wallet.address}")
# 输出: myJCL... (测试网地址)

# AI 查询余额
balance = wallet.get_balance()
print(f"我有 {balance} BTC")

# AI 自主支付服务费用
wallet.send(
    to_address="mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB",
    amount_btc=0.001
)
```

### 与 LLM 集成（Function Calling）

```python
# 让 GPT/Claude 直接控制钱包

TOOLS = [{
    "name": "btc_wallet",
    "description": "比特币钱包操作",
    "parameters": {
        "action": {"enum": ["get_balance", "send", "create_address"]},
        "to_address": {"type": "string"},
        "amount_btc": {"type": "number"}
    }
}]

# LLM 决策 → 调用钱包 → 自动执行
```

---

## 🎯 核心特性

| 特性 | 说明 | 对 AI 的意义 |
|------|------|-------------|
| 🤖 **AI-Native** | JSON 接口设计，完美适配 LLM | AI 可以直接调用，无需解析复杂输出 |
| 🔑 **自托管** | AI 自己掌管私钥 | 真正的经济自主权，不依赖人类 |
| ⚡ **轻量级** | 无需本地全节点 | 云端 AI 也能运行，资源消耗低 |
| 🧪 **测试网优先** | 默认 testnet，安全实验 | AI 可以安全学习和测试 |
| 🔗 **区块链原生** | 直接使用比特币网络 | 全球可访问，无需银行账户 |

---

## 💡 应用场景

### 1. AI 即服务 (AIaaS) 
```
用户 → 支付 0.001 BTC → AI Agent → 提供分析报告
```
AI 自主接收付款，无需人类财务干预

### 2. AI-to-AI 经济
```
AI Agent A ──0.005 BTC──→ AI Agent B
          ←──数据服务────
```
AI 之间直接交易，自动结算

### 3. 自治组织贡献
```
AI 成员完成工作 → 自动获得 BTC 报酬
```
DAO 中的 AI 成员可以持有和交易资产

### 4. 预测市场 Agent
```
AI 分析数据 → 做出预测 → 自动下注 → 自动收款
```
全自动的预测市场参与

---

## 🏗️ 架构

```
┌─────────────────────────────────────────┐
│           Your AI Agent (GPT/Claude)    │
│                 ↓ JSON                  │
├─────────────────────────────────────────┤
│  agent_interface.py  -  AI 友好接口层    │
├─────────────────────────────────────────┤
│  wallet_core.py      -  密钥 & 地址管理  │
├─────────────────────────────────────────┤
│  transaction.py      -  交易构建 & 签名  │
├─────────────────────────────────────────┤
│  blockchain_api.py   -  mempool.space    │
└─────────────────────────────────────────┘
```

**设计哲学**: 让 AI 像调用普通 Python 函数一样使用比特币

---

## 📊 对比其他方案

| 方案 | 需要人类 | 托管风险 | 集成难度 | 适用场景 |
|------|---------|---------|---------|---------|
| 交易所 API | ✅ 需要 | ⚠️ 高 | 中 | 人类交易 |
| 托管钱包 | ✅ 需要 | ⚠️ 高 | 低 | 简单应用 |
| **本方案** | ❌ 不需要 | ✅ 低 | ✅ 极低 | **AI Agent** |

---

## 🛡️ 安全

- ✅ 默认使用测试网，资金安全
- ✅ 私钥本地生成，不上传服务器
- ✅ 支持 WIF 导入/导出，便于备份
- ⚠️ 生产环境建议使用 HSM 或 MPC

---

## 🌟 为什么是这个项目？

> "AI 需要有自己的钱包，就像人类需要有自己的银行账户一样。"

当前 AI 的痛点：
- ❌ 依赖人类进行支付
- ❌ 无法自主参与经济活动
- ❌ 被锁定在平台经济中

本项目的愿景：
- ✅ AI 拥有真正的经济自主权
- ✅ AI 可以成为独立的经济实体
- ✅ AI 与人类平等参与市场经济

---

## 🤝 加入建设

这是 AI 经济基础设施的早期探索。我们需要：

- 💻 开发者：改进代码，添加功能
- 🧠 AI 研究者：探索 AI 经济行为
- 🎨 设计师：让工具更易用
- 📢 传播者：让更多人知道

**一起讨论**: [GitHub Issues](https://github.com/chriswangcq/btc-wallet-for-agent/issues)

---

## 📜 许可

MIT License - 自由使用，共同建设 AI 的加密经济未来

---

<p align="center">
  <b>🚀 让 AI 拥有钱包，让世界拥有更智能的经济 🚀</b>
</p>
