# coding=utf-8
from django.core.files.storage import Storage

from contents.index import index


# noinspection PyAbstractClass,PyUnusedLocal
class ClientStorage(Storage):
    """创建storage"""

    def __init__(self, conf_path=None, ip=None):
        self.conf_path = conf_path or index.FDFS_CLIENT_CONF
        self.ip = ip or index.FDFS_URL

    def _open(self):
        pass

    def _save(self, name, content, max_length=None):
        from fdfs_client.client import Fdfs_client
        client = Fdfs_client(self.conf_path)
        data_byte = content.read()
        result = client.upload_by_buffer(data_byte)
        if result.get("Status") == "Upload successed.":
            return result.get("Remote file_id")
        return Exception("上传失败!")

    def exists(self, name):
        """存在时操作"""
        return False

    def url(self, name):
        """拼接url"""
        return self.ip + name
