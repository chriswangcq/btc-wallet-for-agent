"""
区块链API交互模块
提供余额查询、UTXO获取、交易广播等功能
使用公开的区块链API，无需本地节点
"""

import requests
import json
from typing import Dict, List, Optional, Any

class BlockchainAPI:
    """区块链API客户端"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        # 使用 mempool.space API (免费，无需API key)
        if testnet:
            self.base_url = "https://mempool.space/testnet/api"
        else:
            self.base_url = "https://mempool.space/api"
    
    def get_balance(self, address: str) -> Dict[str, Any]:
        """
        获取地址余额
        
        Returns:
            {
                'address': str,
                'chain_stats': {...},
                'mempool_stats': {...},
                'balance_satoshi': int,
                'balance_btc': float
            }
        """
        url = f"{self.base_url}/address/{address}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 计算总余额
            funded = data['chain_stats']['funded_txo_sum']
            spent = data['chain_stats']['spent_txo_sum']
            balance_satoshi = funded - spent
            
            return {
                'address': address,
                'chain_stats': data['chain_stats'],
                'mempool_stats': data['mempool_stats'],
                'balance_satoshi': balance_satoshi,
                'balance_btc': balance_satoshi / 100_000_000
            }
        except requests.exceptions.RequestException as e:
            return {'error': f'API请求失败: {str(e)}', 'address': address}
    
    def get_utxos(self, address: str) -> List[Dict]:
        """
        获取地址的UTXO列表
        
        Returns:
            [
                {
                    'txid': str,
                    'vout': int,
                    'value': int,  # satoshi
                    'status': {...}
                },
                ...
            ]
        """
        url = f"{self.base_url}/address/{address}/utxo"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            utxos = response.json()
            
            # 格式化输出
            formatted_utxos = []
            for utxo in utxos:
                formatted_utxos.append({
                    'txid': utxo['txid'],
                    'vout': utxo['vout'],
                    'value': utxo['value'],
                    'value_btc': utxo['value'] / 100_000_000,
                    'status': utxo.get('status', {})
                })
            return formatted_utxos
        except requests.exceptions.RequestException as e:
            return [{'error': f'API请求失败: {str(e)}'}]
    
    def get_transaction(self, txid: str) -> Dict:
        """获取交易详情"""
        url = f"{self.base_url}/tx/{txid}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'API请求失败: {str(e)}', 'txid': txid}
    
    def get_fee_estimates(self) -> Dict[str, int]:
        """
        获取推荐的手续费率 (sat/vB)
        
        Returns:
            {
                'fastestFee': int,      # ~10分钟
                'halfHourFee': int,     # ~30分钟
                'hourFee': int,         # ~1小时
                'economyFee': int,      # ~节省模式
                'minimumFee': int       # 最低
            }
        """
        url = f"{self.base_url}/v1/fees/recommended"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'API请求失败: {str(e)}'}
    
    def get_block_height(self) -> int:
        """获取当前区块高度"""
        url = f"{self.base_url}/blocks/tip/height"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return int(response.text)
        except requests.exceptions.RequestException as e:
            return -1
    
    def broadcast_transaction(self, raw_tx_hex: str) -> Dict:
        """
        广播交易到网络
        
        Args:
            raw_tx_hex: 签名后的交易十六进制字符串
            
        Returns:
            {'success': True, 'txid': str} 或 {'success': False, 'error': str}
        """
        url = f"{self.base_url}/tx"
        try:
            response = requests.post(url, data=raw_tx_hex, timeout=30)
            response.raise_for_status()
            txid = response.text.strip()
            return {
                'success': True,
                'txid': txid,
                'explorer_url': f"https://mempool.space/{'testnet/' if self.testnet else ''}tx/{txid}"
            }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e.response, 'text'):
                error_msg = e.response.text
            return {'success': False, 'error': error_msg}
    
    def get_address_history(self, address: str, limit: int = 10) -> List[Dict]:
        """获取地址的交易历史"""
        # 使用scripthash endpoint获取交易历史
        # 需要先将地址转换为scripthash
        url = f"{self.base_url}/address/{address}/txs"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            txs = response.json()
            
            formatted_txs = []
            for tx in txs[:limit]:
                formatted_txs.append({
                    'txid': tx['txid'],
                    'status': tx.get('status', {}),
                    'fee': tx.get('fee', 0),
                    'vsize': tx.get('vsize', 0),
                    'explorer_url': f"https://mempool.space/{'testnet/' if self.testnet else ''}tx/{tx['txid']}"
                })
            return formatted_txs
        except requests.exceptions.RequestException as e:
            return [{'error': f'API请求失败: {str(e)}'}]


# 备用API: BlockCypher (需要API key for high limits)
class BlockCypherAPI:
    """BlockCypher API客户端 (备用)"""
    
    def __init__(self, token: str = None, testnet: bool = True):
        self.token = token
        self.testnet = testnet
        self.coin = 'btc-testnet' if testnet else 'btc'
        self.base_url = f"https://api.blockcypher.com/v1/{self.coin}/main"
    
    def get_balance(self, address: str) -> Dict:
        """获取地址余额"""
        url = f"{self.base_url}/addrs/{address}/balance"
        if self.token:
            url += f"?token={self.token}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'address': address,
                'balance_satoshi': data['balance'],
                'balance_btc': data['balance'] / 100_000_000,
                'unconfirmed_balance': data['unconfirmed_balance'],
                'final_balance': data['final_balance'],
                'n_tx': data['n_tx']
            }
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


if __name__ == '__main__':
    print("=" * 60)
    print("区块链API模块测试")
    print("=" * 60)
    
    # 使用测试网
    api = BlockchainAPI(testnet=True)
    
    print("\n📊 当前区块高度:")
    height = api.get_block_height()
    print(f"   {height}")
    
    print("\n⛽ 推荐手续费 (sat/vB):")
    fees = api.get_fee_estimates()
    if 'error' not in fees:
        print(f"   快速确认 (~10分钟): {fees.get('fastestFee', 'N/A')} sat/vB")
        print(f"   普通确认 (~30分钟): {fees.get('halfHourFee', 'N/A')} sat/vB")
        print(f"   慢速确认 (~1小时): {fees.get('hourFee', 'N/A')} sat/vB")
        print(f"   经济模式: {fees.get('economyFee', 'N/A')} sat/vB")
    else:
        print(f"   错误: {fees['error']}")
    
    # 测试查询一个已知测试网地址
    test_address = "tb1qtestaddress1234567890abcdef"  # 这是一个示例地址
    print(f"\n💰 测试地址余额查询 ({test_address[:20]}...):")
    balance = api.get_balance(test_address)
    if 'error' not in balance:
        print(f"   余额: {balance['balance_btc']:.8f} BTC ({balance['balance_satoshi']} sat)")
        print(f"   交易数: {balance['chain_stats'].get('tx_count', 'N/A')}")
    else:
        print(f"   {balance['error']}")
    
    print("\n" + "=" * 60)
