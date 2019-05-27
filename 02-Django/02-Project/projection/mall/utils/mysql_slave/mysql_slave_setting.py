# coding = utf-8

# noinspection PyMethodMayBeStatic
class MasterSlaveRouter(object):
    """主从分离读写"""

    def db_for_read(self, model, **hints):
        """读"""
        return "slave"

    def db_for_write(self, model, **hints):
        """写"""
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """是否关联运行"""
        return True
