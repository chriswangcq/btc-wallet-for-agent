# BTC Wallet for AI Agent 🤖 ₿

专为AI Agent设计的比特币钱包工具，提供JSON接口，便于程序化调用。

## 特性

- ✅ **AI友好** - JSON输入/输出，易于AI Agent集成
- ✅ **无需全节点** - 使用mempool.space API，零配置
- ✅ **完整功能** - 创建/导入钱包、查询余额、发送交易
- ✅ **测试网支持** - 默认使用测试网，安全开发
- ✅ **交易签名** - 本地签名，私钥不离开本地

## 安装

```bash
git clone https://github.com/chriswangcq/btc-wallet-for-agent.git
cd btc-wallet-for-agent
pip install -r requirements.txt
```

## 快速开始

### Python API

```python
from agent_interface import AgentWallet

# 创建钱包
wallet = AgentWallet(testnet=True)
result = wallet.create_wallet()
print(result)

# 获取余额
balance = wallet.get_balance()
print(balance)
```

### 命令行

```bash
# 交互模式
python agent_interface.py

# 文件模式
python agent_interface.py command.json
```

### JSON接口

```bash
# 创建钱包
echo '{"action": "create_wallet", "testnet": true}' | python agent_interface.py

# 查询网络信息
echo '{"action": "get_network_info"}' | python agent_interface.py

# 获取余额（需先加载钱包）
echo '{"action": "get_balance"}' | python agent_interface.py

# 发送交易
echo '{"action": "send", "to_address": "mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB", "amount_btc": 0.001}' | python agent_interface.py
```

## API参考

### 动作列表

| 动作 | 描述 | 参数 |
|------|------|------|
| `create_wallet` | 创建新钱包 | `testnet` (bool) |
| `import_wallet` | 从WIF导入 | `wif` (string) |
| `import_from_hex` | 从私钥导入 | `private_key_hex` (string) |
| `get_balance` | 查询余额 | - |
| `get_utxos` | 获取UTXO列表 | - |
| `get_transaction_history` | 交易历史 | `limit` (int) |
| `send` | 发送比特币 | `to_address`, `amount_btc`, `fee_rate` (可选) |
| `get_network_info` | 网络信息 | - |
| `get_status` | 钱包状态 | - |

### 响应格式

```json
{
  "success": true,
  "action": "create_wallet",
  "data": {
    "network": "testnet",
    "address": "mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB",
    "public_key": "...",
    "private_key_hex": "...",
    "wif": "..."
  }
}
```

## 架构

```
┌─────────────────┐
│  agent_interface │  ← JSON接口层
├─────────────────┤
│   wallet_core   │  ← 密钥管理、地址生成
├─────────────────┤
│  transaction   │  ← 交易构建、签名
├─────────────────┤
│ blockchain_api │  ← 区块链数据查询
└─────────────────┘
```

## 安全提示

⚠️ **警告**: 本工具用于开发和测试目的
- 默认使用**测试网**(testnet)
- 主网使用前请充分测试
- 妥善保管私钥和WIF

## 测试网水龙头

获取测试币：
- https://mempool.space/testnet/faucet
- https://testnet-faucet.mempool.co/

## 许可证

MIT License
