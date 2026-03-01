"""
AI Agent友好的比特币钱包接口
提供JSON输入/输出，便于AI Agent调用
"""

import json
import sys
from typing import Dict, Any, List
from wallet_core import BitcoinWallet
from blockchain_api import BlockchainAPI
from transaction import create_transaction

class AgentWallet:
    """为AI Agent设计的比特币钱包接口"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.api = BlockchainAPI(testnet=testnet)
        self.wallet = None
    
    def create_wallet(self) -> Dict[str, Any]:
        """创建新钱包"""
        self.wallet = BitcoinWallet(testnet=self.testnet)
        return {
            'success': True,
            'action': 'create_wallet',
            'data': self.wallet.get_info()
        }
    
    def import_wallet(self, wif: str) -> Dict[str, Any]:
        """从WIF导入钱包"""
        try:
            self.wallet = BitcoinWallet.from_wif(wif, testnet=self.testnet)
            return {
                'success': True,
                'action': 'import_wallet',
                'data': self.wallet.get_info()
            }
        except Exception as e:
            return {
                'success': False,
                'action': 'import_wallet',
                'error': str(e)
            }
    
    def import_from_hex(self, private_key_hex: str) -> Dict[str, Any]:
        """从十六进制私钥导入"""
        try:
            self.wallet = BitcoinWallet(private_key_hex=private_key_hex, testnet=self.testnet)
            return {
                'success': True,
                'action': 'import_from_hex',
                'data': self.wallet.get_info()
            }
        except Exception as e:
            return {
                'success': False,
                'action': 'import_from_hex',
                'error': str(e)
            }
    
    def get_balance(self) -> Dict[str, Any]:
        """获取当前钱包余额"""
        if not self.wallet:
            return {'success': False, 'error': 'No wallet loaded'}
        
        result = self.api.get_balance(self.wallet.address)
        if 'error' in result:
            return {'success': False, 'error': result['error']}
        
        return {
            'success': True,
            'action': 'get_balance',
            'data': result
        }
    
    def get_utxos(self) -> Dict[str, Any]:
        """获取UTXO列表"""
        if not self.wallet:
            return {'success': False, 'error': 'No wallet loaded'}
        
        utxos = self.api.get_utxos(self.wallet.address)
        return {
            'success': True,
            'action': 'get_utxos',
            'data': {
                'address': self.wallet.address,
                'utxos': utxos,
                'count': len(utxos)
            }
        }
    
    def get_transaction_history(self, limit: int = 10) -> Dict[str, Any]:
        """获取交易历史"""
        if not self.wallet:
            return {'success': False, 'error': 'No wallet loaded'}
        
        txs = self.api.get_address_history(self.wallet.address, limit)
        return {
            'success': True,
            'action': 'get_transaction_history',
            'data': {
                'address': self.wallet.address,
                'transactions': txs
            }
        }
    
    def send(self, to_address: str, amount_btc: float, fee_rate: int = None) -> Dict[str, Any]:
        """
        发送比特币
        
        Args:
            to_address: 接收地址
            amount_btc: 发送金额 (BTC)
            fee_rate: 手续费率 (sat/vB), 默认自动获取
        """
        if not self.wallet:
            return {'success': False, 'error': 'No wallet loaded'}
        
        # 获取UTXO
        utxos = self.api.get_utxos(self.wallet.address)
        if not utxos or 'error' in utxos[0]:
            return {'success': False, 'error': 'Failed to get UTXOs or no UTXOs available'}
        
        # 计算金额
        amount_satoshi = int(amount_btc * 100_000_000)
        
        # 获取推荐手续费
        if fee_rate is None:
            fees = self.api.get_fee_estimates()
            fee_rate = fees.get('halfHourFee', 10)
        
        # 估算交易大小 (约150字节 per input + 35 per output + 10 overhead)
        estimated_size = 150 * len(utxos) + 35 * 2 + 10
        fee_satoshi = estimated_size * fee_rate
        
        # 创建交易
        try:
            tx = create_transaction(
                wallet=self.wallet,
                utxos=utxos,
                to_address=to_address,
                amount_satoshi=amount_satoshi,
                fee_satoshi=fee_satoshi
            )
            
            # 广播交易
            result = self.api.broadcast_transaction(tx.to_hex())
            
            if result['success']:
                return {
                    'success': True,
                    'action': 'send',
                    'data': {
                        'txid': result['txid'],
                        'explorer_url': result['explorer_url'],
                        'amount_btc': amount_btc,
                        'fee_satoshi': fee_satoshi,
                        'fee_rate': fee_rate,
                        'from': self.wallet.address,
                        'to': to_address
                    }
                }
            else:
                return {
                    'success': False,
                    'action': 'send',
                    'error': result.get('error', 'Broadcast failed')
                }
        except Exception as e:
            return {
                'success': False,
                'action': 'send',
                'error': str(e)
            }
    
    def get_network_info(self) -> Dict[str, Any]:
        """获取网络信息"""
        height = self.api.get_block_height()
        fees = self.api.get_fee_estimates()
        
        return {
            'success': True,
            'action': 'get_network_info',
            'data': {
                'network': 'testnet' if self.testnet else 'mainnet',
                'block_height': height,
                'fee_estimates': fees
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取钱包状态"""
        if not self.wallet:
            return {
                'success': True,
                'action': 'get_status',
                'data': {
                    'wallet_loaded': False,
                    'network': 'testnet' if self.testnet else 'mainnet'
                }
            }
        
        return {
            'success': True,
            'action': 'get_status',
            'data': {
                'wallet_loaded': True,
                'network': 'testnet' if self.testnet else 'mainnet',
                'address': self.wallet.address
            }
        }


def process_command(command_json: str) -> str:
    """
    处理JSON格式的命令
    
    输入格式: {"action": "create_wallet", "testnet": true}
    输出格式: {"success": true, "action": "create_wallet", "data": {...}}
    """
    try:
        cmd = json.loads(command_json)
    except json.JSONDecodeError as e:
        return json.dumps({'success': False, 'error': f'Invalid JSON: {str(e)}'})
    
    action = cmd.get('action')
    testnet = cmd.get('testnet', True)
    
    # 获取或创建钱包实例
    if not hasattr(process_command, 'wallet_instances'):
        process_command.wallet_instances = {}
    
    instance_id = cmd.get('instance_id', 'default')
    if instance_id not in process_command.wallet_instances:
        process_command.wallet_instances[instance_id] = AgentWallet(testnet=testnet)
    
    wallet = process_command.wallet_instances[instance_id]
    
    # 执行动作
    if action == 'create_wallet':
        result = wallet.create_wallet()
    elif action == 'import_wallet':
        result = wallet.import_wallet(cmd.get('wif'))
    elif action == 'import_from_hex':
        result = wallet.import_from_hex(cmd.get('private_key_hex'))
    elif action == 'get_balance':
        result = wallet.get_balance()
    elif action == 'get_utxos':
        result = wallet.get_utxos()
    elif action == 'get_transaction_history':
        result = wallet.get_transaction_history(cmd.get('limit', 10))
    elif action == 'send':
        result = wallet.send(
            to_address=cmd.get('to_address'),
            amount_btc=cmd.get('amount_btc'),
            fee_rate=cmd.get('fee_rate')
        )
    elif action == 'get_network_info':
        result = wallet.get_network_info()
    elif action == 'get_status':
        result = wallet.get_status()
    else:
        result = {'success': False, 'error': f'Unknown action: {action}'}
    
    return json.dumps(result, indent=2)


if __name__ == '__main__':
    # 命令行模式
    if len(sys.argv) > 1:
        # 从文件读取命令
        with open(sys.argv[1], 'r') as f:
            command = f.read()
        result = process_command(command)
        print(result)
    else:
        # 交互模式
        print("=" * 60)
        print("AI Agent比特币钱包接口")
        print("=" * 60)
        print("\n输入JSON命令，例如:")
        print('  {"action": "create_wallet", "testnet": true}')
        print('  {"action": "get_network_info"}')
        print("\n输入 'quit' 退出\n")
        
        while True:
            try:
                cmd = input("> ")
                if cmd.lower() == 'quit':
                    break
                if not cmd.strip():
                    continue
                
                result = process_command(cmd)
                print(result)
                print()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(json.dumps({'success': False, 'error': str(e)}))
