"""
阿里云 OSS 上传服务
用于 DashScope 语音转写的文件上传
"""

import httpx
import hashlib
import hmac
import base64
import time
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger


class OSSUploader:
    """阿里云 OSS 上传器"""
    
    def __init__(self, access_key_id: str, access_key_secret: str, bucket: str = "dashscope"):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.bucket = bucket
        self.region = "cn-shanghai"
        self.endpoint = f"https://{bucket}.oss-{self.region}.aliyuncs.com"
    
    def _generate_signature(self, method: str, content_md5: str, content_type: str, date: str, resource: str) -> str:
        """生成 OSS 签名"""
        canonicalized_resource = f"/{self.bucket}{resource}"
        string_to_sign = f"{method}\n{content_md5}\n{content_type}\n{date}\n{canonicalized_resource}"
        
        h = hmac.new(
            self.access_key_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        )
        signature = base64.b64encode(h.digest()).decode('utf-8')
        return signature
    
    async def upload_file(self, file_path: str, object_key: str) -> Optional[str]:
        """
        上传文件到 OSS
        
        Args:
            file_path: 本地文件路径
            object_key: OSS 对象键
        
        Returns:
            文件 URL，失败返回 None
        """
        try:
            # 读取文件
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 计算 MD5
            content_md5 = base64.b64encode(hashlib.md5(content).digest()).decode('utf-8')
            
            # 准备请求
            date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
            content_type = 'audio/mpeg' if file_path.endswith('.mp3') else 'audio/wav'
            
            # 生成签名
            signature = self._generate_signature(
                'PUT',
                content_md5,
                content_type,
                date,
                f'/{object_key}'
            )
            
            # 上传文件
            url = f"{self.endpoint}/{object_key}"
            headers = {
                'Authorization': f"OSS {self.access_key_id}:{signature}",
                'Date': date,
                'Content-MD5': content_md5,
                'Content-Type': content_type
            }
            
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.put(url, content=content, headers=headers)
                
                if response.status_code == 200:
                    file_url = f"https://{self.bucket}.oss-{self.region}.aliyuncs.com/{object_key}"
                    logger.info(f"OSS 上传成功：{file_url}")
                    return file_url
                else:
                    logger.error(f"OSS 上传失败：{response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"OSS 上传异常：{e}")
            return None


# 全局实例（延迟初始化）
_oss_uploader = None

def get_oss_uploader(access_key_id: str, access_key_secret: str) -> OSSUploader:
    """获取 OSS 上传器实例"""
    global _oss_uploader
    if _oss_uploader is None:
        _oss_uploader = OSSUploader(access_key_id, access_key_secret)
    return _oss_uploader
