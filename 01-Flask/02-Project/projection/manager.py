from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from view import Handle, db

app = Handle("develop").create_app()

manager = Manager(app)
Migrate(app, db)
manager.add_command("mysql", MigrateCommand)


@manager.option("-n", "-name", dest="name")
@manager.option("-p", "-password", dest="password")
def createsuperuser(name, password):
    """创建管理员"""
    from view.modules.models import User
    if not all([name, password]):
        print("参数不足, 无法创建！")
        print("命令使用实例：\npython manage.py createsuperuser -n name -p password")
        return
    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()


if __name__ == '__main__':
    manager.run()
