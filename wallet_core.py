"""
比特币钱包核心模块
提供密钥管理、地址生成、交易构建和签名功能
"""

import os
import json
import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
from typing import Dict, List, Optional, Tuple
import requests

class BitcoinWallet:
    """比特币钱包核心类"""
    
    def __init__(self, private_key_hex: str = None, testnet: bool = True):
        """
        初始化钱包
        
        Args:
            private_key_hex: 私钥（十六进制字符串），若为None则生成新钱包
            testnet: 是否使用测试网
        """
        self.testnet = testnet
        self.network_byte = b'\x6f' if testnet else b'\x00'  # 测试网:0x6f, 主网:0x00
        self.wif_prefix = b'\xef' if testnet else b'\x80'
        
        if private_key_hex:
            self.private_key = bytes.fromhex(private_key_hex)
        else:
            self.private_key = os.urandom(32)
        
        # 生成公钥
        self.signing_key = SigningKey.from_string(self.private_key, curve=SECP256k1)
        self.verifying_key = self.signing_key.get_verifying_key()
        
        # 未压缩公钥 (0x04 + x + y)
        self.public_key_uncompressed = b'\x04' + self.verifying_key.to_string()
        
        # 压缩公钥
        x = self.verifying_key.to_string()[:32]
        y = self.verifying_key.to_string()[32:]
        prefix = b'\x02' if int.from_bytes(y, 'big') % 2 == 0 else b'\x03'
        self.public_key_compressed = prefix + x
    
    @property
    def private_key_hex(self) -> str:
        """返回十六进制格式的私钥"""
        return self.private_key.hex()
    
    @property
    def wif(self) -> str:
        """返回WIF格式的私钥（用于导入其他钱包）"""
        # WIF = base58check_encode(prefix + private_key + compression_flag)
        extended = self.wif_prefix + self.private_key + b'\x01'
        return self._base58check_encode(extended)
    
    @property
    def address(self) -> str:
        """生成P2PKH地址"""
        # 1. SHA256(public_key)
        sha256_hash = hashlib.sha256(self.public_key_compressed).digest()
        # 2. RIPEMD160(SHA256)
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        hash160 = ripemd160.digest()
        # 3. 添加网络字节
        extended = self.network_byte + hash160
        # 4. Base58Check编码
        return self._base58check_encode(extended)
    
    def _base58check_encode(self, data: bytes) -> str:
        """Base58Check编码"""
        # 计算校验和 (double SHA256)
        checksum = hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]
        # 编码
        return base58.b58encode(data + checksum).decode('ascii')
    
    def get_info(self) -> Dict:
        """获取钱包完整信息"""
        return {
            'network': 'testnet' if self.testnet else 'mainnet',
            'address': self.address,
            'public_key': self.public_key_compressed.hex(),
            'public_key_uncompressed': self.public_key_uncompressed.hex(),
            'private_key_hex': self.private_key_hex,
            'wif': self.wif
        }
    
    def to_json(self) -> str:
        """导出为JSON格式"""
        return json.dumps(self.get_info(), indent=2)
    
    @classmethod
    def from_wif(cls, wif: str, testnet: bool = True) -> 'BitcoinWallet':
        """从WIF导入钱包"""
        decoded = base58.b58decode(wif)
        # 去掉校验和
        payload = decoded[:-4]
        # 验证校验和
        checksum = decoded[-4:]
        computed = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        if checksum != computed:
            raise ValueError("Invalid WIF checksum")
        # 提取私钥
        private_key = payload[1:33]  # 跳过前缀字节
        return cls(private_key.hex(), testnet)
    
    def __str__(self) -> str:
        return f"BitcoinWallet(address={self.address}, network={'testnet' if self.testnet else 'mainnet'})"


def double_sha256(data: bytes) -> bytes:
    """Double SHA256哈希"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def hash160(data: bytes) -> bytes:
    """RIPEMD160(SHA256(data))"""
    sha256_hash = hashlib.sha256(data).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    return ripemd160.digest()


if __name__ == '__main__':
    # 测试
    print("=" * 60)
    print("比特币钱包核心模块测试")
    print("=" * 60)
    
    # 创建新钱包
    wallet = BitcoinWallet(testnet=True)
    info = wallet.get_info()
    
    print("\n📦 新钱包生成:")
    print(f"   网络: {info['network']}")
    print(f"   地址: {info['address']}")
    print(f"   WIF:  {info['wif']}")
    print(f"   公钥: {info['public_key'][:40]}...")
    print(f"   私钥: {info['private_key_hex'][:20]}...")
    
    # 测试从WIF导入
    wallet2 = BitcoinWallet.from_wif(info['wif'], testnet=True)
    print(f"\n🔐 WIF导入测试:")
    print(f"   原地址: {wallet.address}")
    print(f"   导入后: {wallet2.address}")
    print(f"   匹配: {'✓' if wallet.address == wallet2.address else '✗'}")
    
    print("\n" + "=" * 60)
