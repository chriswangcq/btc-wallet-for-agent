"""
比特币交易构建和签名模块
支持创建、签名和序列化比特币交易
"""

import hashlib
import struct
from typing import List, Dict, Tuple, Optional
from wallet_core import BitcoinWallet, hash160, double_sha256

class TransactionInput:
    """交易输入"""
    
    def __init__(self, txid: str, vout: int, value: int, script_pubkey: bytes = None):
        self.txid = txid
        self.vout = vout
        self.value = value  # satoshi
        self.script_pubkey = script_pubkey or b''
        self.script_sig = b''
        self.sequence = 0xffffffff  # 默认序列号
    
    def serialize(self) -> bytes:
        """序列化输入（用于签名前）"""
        # txid (32 bytes, little endian)
        txid_bytes = bytes.fromhex(self.txid)[::-1]
        # vout (4 bytes, little endian)
        vout_bytes = struct.pack('<I', self.vout)
        # script_sig (varint + bytes)
        script_sig_bytes = self.script_sig
        script_sig_len = len(script_sig_bytes)
        if script_sig_len < 0xfd:
            script_len_bytes = bytes([script_sig_len])
        else:
            script_len_bytes = b'\xfd' + struct.pack('<H', script_sig_len)
        # sequence (4 bytes)
        sequence_bytes = struct.pack('<I', self.sequence)
        
        return txid_bytes + vout_bytes + script_len_bytes + script_sig_bytes + sequence_bytes
    
    def serialize_for_signing(self, script_code: bytes) -> bytes:
        """序列化用于签名的输入"""
        txid_bytes = bytes.fromhex(self.txid)[::-1]
        vout_bytes = struct.pack('<I', self.vout)
        # 使用script_code代替script_sig
        script_len = len(script_code)
        if script_len < 0xfd:
            script_len_bytes = bytes([script_len])
        else:
            script_len_bytes = b'\xfd' + struct.pack('<H', script_len)
        sequence_bytes = struct.pack('<I', self.sequence)
        
        return txid_bytes + vout_bytes + script_len_bytes + script_code + sequence_bytes


class TransactionOutput:
    """交易输出"""
    
    def __init__(self, value: int, script_pubkey: bytes):
        self.value = value  # satoshi
        self.script_pubkey = script_pubkey
    
    def serialize(self) -> bytes:
        """序列化输出"""
        # value (8 bytes, little endian)
        value_bytes = struct.pack('<Q', self.value)
        # script_pubkey (varint + bytes)
        script_len = len(self.script_pubkey)
        if script_len < 0xfd:
            script_len_bytes = bytes([script_len])
        else:
            script_len_bytes = b'\xfd' + struct.pack('<H', script_len)
        
        return value_bytes + script_len_bytes + self.script_pubkey


class BitcoinTransaction:
    """比特币交易类"""
    
    def __init__(self, testnet: bool = True, version: int = 2):
        self.version = version
        self.inputs: List[TransactionInput] = []
        self.outputs: List[TransactionOutput] = []
        self.locktime = 0
        self.testnet = testnet
        self.hash_type = 0x01  # SIGHASH_ALL
    
    def add_input(self, txid: str, vout: int, value: int, script_pubkey: bytes = None):
        """添加输入"""
        self.inputs.append(TransactionInput(txid, vout, value, script_pubkey))
    
    def add_output(self, address: str, value: int):
        """添加输出到指定地址"""
        script_pubkey = self._address_to_script_pubkey(address)
        self.outputs.append(TransactionOutput(value, script_pubkey))
    
    def _address_to_script_pubkey(self, address: str) -> bytes:
        """将地址转换为scriptPubKey"""
        # 简化实现：假设是P2PKH地址
        import base58
        
        decoded = base58.b58decode(address)
        # 去掉版本字节和校验和
        hash160_bytes = decoded[1:-4]
        
        # P2PKH script: OP_DUP OP_HASH160 <20 bytes> OP_EQUALVERIFY OP_CHECKSIG
        script = bytes([
            0x76,  # OP_DUP
            0xa9,  # OP_HASH160
            0x14,  # 推送20字节
        ]) + hash160_bytes + bytes([
            0x88,  # OP_EQUALVERIFY
            0xac   # OP_CHECKSIG
        ])
        return script
    
    def sign_input(self, input_index: int, wallet: BitcoinWallet):
        """使用钱包签名指定输入"""
        if input_index >= len(self.inputs):
            raise ValueError("Invalid input index")
        
        inp = self.inputs[input_index]
        
        # 创建script_code (P2PKH)
        public_key_hash = hash160(wallet.public_key_compressed)
        script_code = bytes([0x76, 0xa9, 0x14]) + public_key_hash + bytes([0x88, 0xac])
        
        # 构建用于签名的数据
        hash_to_sign = self._get_hash_for_signature(input_index, script_code)
        
        # 签名
        signature = wallet.signing_key.sign_digest(hash_to_sign, sigencode=lambda sig, _: sig)
        # 添加SIGHASH_ALL
        signature = signature + bytes([self.hash_type])
        
        # 构建scriptSig: <sig> <pubkey>
        sig_len = len(signature)
        pubkey_len = len(wallet.public_key_compressed)
        inp.script_sig = bytes([sig_len]) + signature + bytes([pubkey_len]) + wallet.public_key_compressed
    
    def _get_hash_for_signature(self, input_index: int, script_code: bytes) -> bytes:
        """获取需要签名的哈希"""
        # 序列化交易用于签名
        tx_data = self._serialize_for_signing(input_index, script_code)
        return double_sha256(tx_data)
    
    def _serialize_for_signing(self, input_index: int, script_code: bytes) -> bytes:
        """序列化交易用于签名"""
        # version
        result = struct.pack('<I', self.version)
        # input count
        result += bytes([len(self.inputs)])
        # inputs
        for i, inp in enumerate(self.inputs):
            if i == input_index:
                result += inp.serialize_for_signing(script_code)
            else:
                # 其他输入的script_sig为空
                empty_inp = TransactionInput(inp.txid, inp.vout, inp.value)
                result += empty_inp.serialize()
        # output count
        result += bytes([len(self.outputs)])
        # outputs
        for out in self.outputs:
            result += out.serialize()
        # locktime
        result += struct.pack('<I', self.locktime)
        # hash type
        result += struct.pack('<I', self.hash_type)
        
        return result
    
    def serialize(self) -> bytes:
        """序列化完整交易"""
        # version
        result = struct.pack('<I', self.version)
        # input count
        result += bytes([len(self.inputs)])
        # inputs
        for inp in self.inputs:
            result += inp.serialize()
        # output count
        result += bytes([len(self.outputs)])
        # outputs
        for out in self.outputs:
            result += out.serialize()
        # locktime
        result += struct.pack('<I', self.locktime)
        
        return result
    
    def to_hex(self) -> str:
        """返回十六进制格式的交易"""
        return self.serialize().hex()
    
    def get_txid(self) -> str:
        """计算交易ID (double SHA256, little endian)"""
        tx_hash = double_sha256(self.serialize())
        return tx_hash[::-1].hex()
    
    def get_size(self) -> int:
        """获取交易大小（字节）"""
        return len(self.serialize())
    
    def get_fee(self) -> int:
        """计算手续费 (输入总额 - 输出总额)"""
        input_sum = sum(inp.value for inp in self.inputs)
        output_sum = sum(out.value for out in self.outputs)
        return input_sum - output_sum


def create_transaction(
    wallet: BitcoinWallet,
    utxos: List[Dict],
    to_address: str,
    amount_satoshi: int,
    fee_satoshi: int
) -> BitcoinTransaction:
    """
    创建并签名交易
    
    Args:
        wallet: 发送方钱包
        utxos: 可用的UTXO列表
        to_address: 接收地址
        amount_satoshi: 发送金额 (satoshi)
        fee_satoshi: 手续费 (satoshi)
    
    Returns:
        签名后的交易对象
    """
    tx = BitcoinTransaction(testnet=wallet.testnet)
    
    # 计算需要的输入总额
    total_needed = amount_satoshi + fee_satoshi
    total_input = 0
    
    # 选择UTXO
    for utxo in utxos:
        if total_input >= total_needed:
            break
        
        tx.add_input(
            txid=utxo['txid'],
            vout=utxo['vout'],
            value=utxo['value']
        )
        total_input += utxo['value']
    
    if total_input < total_needed:
        raise ValueError(f"余额不足: 需要 {total_needed}, 可用 {total_input}")
    
    # 添加输出
    tx.add_output(to_address, amount_satoshi)
    
    # 找零
    change = total_input - total_needed
    if change > 546:  # dust limit
        tx.add_output(wallet.address, change)
    
    # 签名所有输入
    for i in range(len(tx.inputs)):
        tx.sign_input(i, wallet)
    
    return tx


if __name__ == '__main__':
    print("=" * 60)
    print("交易构建模块测试")
    print("=" * 60)
    
    from wallet_core import BitcoinWallet
    
    # 创建测试钱包
    wallet = BitcoinWallet(testnet=True)
    print(f"\n📦 发送方钱包: {wallet.address}")
    
    # 创建交易（使用假UTXO，仅用于测试结构）
    tx = BitcoinTransaction(testnet=True)
    tx.add_input(
        txid="1234567890abcdef" * 4,
        vout=0,
        value=100000
    )
    tx.add_output("mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB", 50000)  # 测试网地址
    tx.add_output(wallet.address, 48000)  # 找零
    
    print(f"\n📝 交易结构:")
    print(f"   版本: {tx.version}")
    print(f"   输入数: {len(tx.inputs)}")
    print(f"   输出数: {len(tx.outputs)}")
    print(f"   大小: {tx.get_size()} bytes")
    
    print(f"\n🔐 交易序列化 (hex, 前100字符):")
    print(f"   {tx.to_hex()[:100]}...")
    
    print("\n" + "=" * 60)
