"""
基础使用示例 - 展示 AI Agent 如何使用 BTC 钱包
"""
import sys
sys.path.insert(0, '..')

from agent_interface import AgentWallet
import json

def main():
    print("=" * 60)
    print("🤖 BTC Wallet for AI Agents - 基础示例")
    print("=" * 60)
    
    # 1. 创建钱包
    print("\n📦 步骤 1: 创建新钱包...")
    wallet = AgentWallet(testnet=True)
    result = wallet.create_wallet()
    
    if result['success']:
        print(f"✅ 钱包创建成功!")
        print(f"   地址: {result['data']['address']}")
        print(f"   公钥: {result['data']['public_key'][:20]}...")
        print(f"   WIF: {result['data']['wif'][:15]}...")
    else:
        print(f"❌ 创建失败: {result.get('error')}")
        return
    
    # 2. 查询余额
    print("\n💰 步骤 2: 查询余额...")
    balance = wallet.get_balance()
    
    if balance['success']:
        print(f"✅ 余额查询成功!")
        print(f"   余额: {balance['data']['balance_btc']} BTC")
        print(f"   地址: {balance['data']['address']}")
        print(f"   UTXO 数量: {balance['data']['utxo_count']}")
    else:
        print(f"❌ 查询失败: {balance.get('error')}")
    
    # 3. 获取网络信息
    print("\n🌐 步骤 3: 获取网络信息...")
    network_info = wallet.get_network_info()
    
    if network_info['success']:
        print(f"✅ 网络信息获取成功!")
        print(f"   网络: {network_info['data']['network']}")
        print(f"   当前区块高度: {network_info['data']['block_height']}")
        print(f"   推荐手续费: {network_info['data']['recommended_fees']['fastest']} sat/vB")
    
    # 4. 保存钱包信息（实际项目中请妥善保管）
    print("\n💾 步骤 4: 保存钱包信息到文件...")
    wallet_info = {
        'address': result['data']['address'],
        'public_key': result['data']['public_key'],
        'wif': result['data']['wif'],
        'network': 'testnet'
    }
    
    with open('my_wallet.json', 'w') as f:
        json.dump(wallet_info, f, indent=2)
    print("✅ 钱包信息已保存到 my_wallet.json")
    print("⚠️  警告: 请妥善保管此文件，包含私钥信息！")
    
    print("\n" + "=" * 60)
    print("🎉 示例完成!")
    print("=" * 60)
    print(f"\n提示: 访问 https://mempool.space/testnet/faucet")
    print(f"获取测试币到地址: {result['data']['address']}")

if __name__ == "__main__":
    main()
