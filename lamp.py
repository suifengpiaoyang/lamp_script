#!/usr/bin/python
# coding=utf-8

'''
os:centos7

python version:2.x

name:LAMP 辅助安装脚本

author:Zhang

last_edit:2019-4-16

version：1.0.2
version:1.0.3 增加端口号的 udp 设置，以便方便游戏加速

'''


import os
import re
import sys
import socket


class Apache:

    def __init__(self):

        pass

    def install(self):

        cmd = 'yum install httpd -y'
        os.system(cmd)

    def remove(self):
        'remove_apache'

        self.close()
        cmd = 'yum remove httpd'
        os.system(cmd)
        self.close_port()

    def start(self):

        cmd = 'systemctl start httpd'
        os.system(cmd)

    def close(self):

        cmd = 'systemctl stop httpd'
        os.system(cmd)

    def restart(self):

        cmd = 'systemctl restart httpd'
        os.system(cmd)

    def open_port(self):

        cmd = '''
              firewall-cmd --add-port=80/tcp --permanent
              firewall-cmd --add-port=443/tcp --permanent
              firewall-cmd --reload
              '''
        os.popen(cmd)

    def close_port(self):

        cmd = '''
              firewall-cmd --remove-port=80/tcp --permanent
              firewall-cmd --remove-port=443/tcp --permanent
              firewall-cmd --reload
              '''
        os.popen(cmd)

    def attr_config(self):

        path = '/etc/httpd/conf/httpd.conf'
        if os.path.exists(path):
            cmd = 'vi /etc/httpd/conf/httpd.conf'
            os.system(cmd)
        else:
            print '请先安装 Apache.'

    def show_virtualhost_message(self):

        cmd = 'httpd -S'
        os.system(cmd)
        raw_input('\n请按Enter继续...')

    def show_status(self):

        cmd = 'systemctl status httpd'
        os.system(cmd)

    def auto_start(self):

        cmd = 'systemctl enable httpd'
        os.system(cmd)

    def one_key(self):
        '一键安装：包含 安装，启动服务，设置开机启动，开启端口'
        self.install()
        self.open_port()
        self.auto_start()
        self.start()

    def display(self):

        while True:
            string = '''
            ***************************

                    Apache 配置

            ***************************

                1.安装 Apache；
                2.启动 Apache 服务；
                3.关闭 Apache 服务；
                4.重启 Apache 服务；
                5.卸载 Apache；
                6.手动修改 Apache 配置；
                7.显示虚拟配置信息；
                9.Apache 一键安装配置；
                0.返回上一页；
            '''
            print string
            flag = raw_input('请选择：')
            if flag == '1':
                self.install()
            elif flag == '2':
                self.start()
            elif flag == '3':
                self.close()
            elif flag == '4':
                self.restart()
            elif flag == '5':
                flag = raw_input('是否确定要卸载 Apache[y/n]？')
                if flag == 'y':
                    self.remove()
                    print '卸载成功。'
            elif flag == '6':
                self.attr_config()
            elif flag == '7':
                self.show_virtualhost_message()
            elif flag == '9':
                self.one_key()
            elif flag == '0' or flag == '':
                break
            else:
                print '请输入正确的序号'


class MySQL:

    def __init__(self):

        pass

    def install(self):
        'install MySQL5.7'

        # 下载 MySQL 的 yum 源
        cmd = "wget 'https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm'"
        os.system(cmd)

        # 安装该 yum 源
        cmd = 'rpm -Uvh mysql57-community-release-el7-11.noarch.rpm'
        os.system(cmd)
        # 安装 mysql
        cmd = 'yum install mysql-community-server -y'
        os.system(cmd)

    def remove(self):
        'remove MySQL'

        self.close()
        cmd = 'yum remove mysql-community-server'
        os.system(cmd)
        self.close_port()

    def start(self):

        cmd = 'systemctl start mysqld'
        os.system(cmd)

    def close(self):

        cmd = 'systemctl stop mysqld'
        os.system(cmd)

    def restart(self):

        cmd = 'systemctl restart mysqld'
        os.system(cmd)

    def open_port(self):

        cmd = '''
              firewall-cmd --add-port=3306/tcp --permanent
              firewall-cmd --reload
              '''
        os.popen(cmd)

    def close_port(self):

        cmd = '''
              firewall-cmd --remove-port=3306/tcp --permanent
              firewall-cmd --reload
              '''
        os.popen(cmd)

    def close_password_policy_plugin(self):
        '关闭密码策略插件，以便方便设置密码。'
        filepath = '/etc/my.cnf'
        with open(filepath, 'a+')as fl:
            fl.seek(0)
            file_data = fl.read()
            mo = re.findall(r'(?<!# )validate_password=off', file_data)
            if len(mo) == 0:
                print '密码管理策略插件关闭中...'
                fl.write('validate_password=off' + '\n')
                print '密码管理策略插件已成功关闭。'
            else:
                print '管理密码插件本已关闭，无需进行操作。'
        self.restart()

    def get_default_password(self):

        cmd = "grep 'temporary password' /var/log/mysqld.log"
        result = os.popen(cmd).read()
        default_password = re.findall(r'root@localhost:\s*(.*)', result)
        if len(default_password) != 0:
            return default_password[0]
        else:
            return None

    def change_password(self,user,old_password,new_password):

        cmd = 'mysqladmin -u"{}" -p"{}" password "{}"'.format(user, old_password, new_password)
        os.system(cmd)

    def login(self,user,password):

        cmd = 'mysql -u"{}" -p"{}"'.format(user,password)
        os.system(cmd)

    def one_key(self):
        '包含 MySQL 下载，启动，禁止密码策略插件，打开远程端口'

        while(True):
            new_password = raw_input('请设置mysql的密码：')
            flag = raw_input('确定将root密码设置为：{}【y/n】？'.format(new_password))
            if flag == 'y':
                raw_input('请务必记好设置好的密码。如果已经记好，请按Enter开始安装。')
                break

        self.install()
        self.open_port()
        self.start()
        self.close_password_policy_plugin()
        default_password = self.get_default_password()
        self.change_password('root', default_password, new_password)
        cmd = 'rm -rf mysql57-community-release-el7-11.noarch.rpm'
        os.system(cmd)

    def display(self):

        while True:
            string = '''
            ***************************

                    MySQL 配置

            ***************************

                1.安装 MySQL；
                2.启动 MySQL 服务；
                3.关闭 MySQL 服务；
                4.重启 MySQL 服务；
                5.卸载 MySQL；
                6.账号登录；
                7.修改账号密码；
                9.一键安装配置 MySQL ；
                10.关闭密码管理策略插件；
                11.显示初始账户密码；
                0.返回上一页；
            '''
            print string
            flag = raw_input('请选择：')

            if flag == '1':
                self.install()
                print '安装成功。'

            elif flag == '2':
                self.start()

            elif flag == '3':
                self.close()

            elif flag == '4':
                self.restart()

            elif flag == '5':
                flag = raw_input('是否确定要卸载 MySQL[y/n]？')
                if flag == 'y':
                    self.remove()
                    print '卸载成功。'

            elif flag == '6':
                user = raw_input('请输入用户名：')
                password = raw_input('请输入密码：')
                self.login(user, password)

            elif flag == '7':
                user = raw_input('请输入要修改密码的用户名：')
                old_password = raw_input('请输入初始密码：')
                new_password = raw_input('请输入更新后的密码：')
                flag = raw_input('是否确定更改(y/n)？')
                if flag == 'y':
                    self.change_password(user, old_password, new_password)
                else:
                    pass

            elif flag == '9':
                self.one_key()

            elif flag == '10':
                self.close_password_policy_plugin()

            elif flag == '11':
                default_password = self.get_default_password()
                if(default_password):
                    print '初始账户：root'
                    print '初始密码：{}'.format(default_password)
                else:
                    print '获得初始密码失败。'

            elif flag == '0' or flag == '':
                break
            else:
                print '请输入正确的序号'


class PHP:

    # php 使用 7.1 版本，以适应ssrpanel的需要
    def __init__(self):
        pass

    def install(self):

        cmd = 'yum install git zip unzip -y'
        os.system(cmd)
        
        # 升级 yum 源
        cmd = '''
            rpm -Uvh https://mirror.webtatic.com/yum/el7/epel-release.rpm
            rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm
        '''
        os.system(cmd)

        #安装 php7.1 和 php7.1-fpm
        cmd = 'yum install php71w-devel php71w-fpm -y'
        os.system(cmd)

    def install_all_plugins(self):
   
        # 安装 php71的所有插件，但是因为 php71 Apache 插件名称问题，所以在下面另行安装
        # 同时以为 mysql 插件不兼容，所以无法安装，但是默认安装了 mysqld.
        cmd = 'yum install php71w* --skip-broken -y'
        os.system(cmd)

        # 安装 Apache 插件并挂载
        cmd = 'yum install mod_php71w.x86_64 -y'
        os.system(cmd)

    def show_installed_plugins(self):
        cmd = 'php -m'
        os.system(cmd)
        raw_input('请按 Enter 继续...')

    def remove(self):

        # 要卸载，首先需要将挂载Apache的部分删除，再卸载插件，最后卸载本体
        cmd = 'yum remove mod_php71w.x86_64 php71w* php71w-devel php71w-fpm -y'
        os.system(cmd)

    def start(self):

        cmd = 'systemctl start php-fpm'
        os.system(cmd)

    def close(self):

        cmd = 'systemctl stop php-fpm'
        os.system(cmd)

    def restart(self):

        cmd = 'systemctl restart php-fpm'
        os.system(cmd)

    def auto_start(self):
        cmd = 'systemctl enable php-fpm'
        os.system(cmd)

    def open_port(self):
        pass

    def one_key(self):
        self.install()
        self.install_all_plugins()
        self.auto_start()

    def display(self):

        while True:
            string = '''
            **********************

                    PHP配置

            **********************

                1.安装 php ；
                2.启动 php；
                3.关闭 php；
                4.重启 php；
                5.卸载 php；
                6.列出已安装的 php 插件；
                9.一键安装配置 php；
                0.返回上一页；
            '''
            print string
            flag = raw_input('请选择：')
            if flag == '1':
                self.install()
                self.install_all_plugins()
            elif flag == '2':
                self.start()
            elif flag == '3':
                self.close()
            elif flag == '4':
                self.restart()
            elif flag == '5':
                flag = raw_input('是否确定要卸载 PHP[y/n]？')
                if flag == 'y':
                    self.remove()
                    print '卸载成功。'
            elif flag == '6':
                self.show_installed_plugins()
            elif flag == '9':
                self.one_key()
            elif flag == '0' or flag == '':
                break
            else:
                print '请输入正确的序号'

class PHPMyAdmin:

    def __init__(self):
        pass

    def install(self):

        cmd = 'yum install phpmyadmin -y'
        os.system(cmd)

    def remove(self):
        'remove_phpmyadmin'

        cmd = 'yum remove phpmyadmin'
        os.system(cmd)

    def attr_config(self):

        path = '/etc/httpd/conf.d/phpMyAdmin.conf'
        if os.path.exists(path):
            cmd = 'vi {}'.format(path)
            os.system(cmd)
        else:
            print '没有找到 phpmyadmin 的配置文件。'

    def __auto_config(self):
        
        """
        将 Require ip 127.0.0.1 和 Require ip ::1 注释掉，
        并在 </RequireAny> 前面一行加上 Require all granted
        """
        path = '/etc/httpd/conf.d/phpMyAdmin.conf'
        if not os.path.exists(path):
            print '请先安装 phpMyAdmin'
        else:
            with open(path)as fl:
                data = fl.readlines()
            with open(path,'w')as fl:
                for line in data:
                    if 'Require ip' in line:
                        index = data.index(line)
                        replace_str = line.replace('Require ip','# Require ip')
                        fl.write(replace_str) 
                    elif r'</RequireAny>' in line:
                        fl.write(r'      Require all granted' + '\n')
                        fl.write(line + '\n')
                    else:
                        fl.write(line)

    def one_key(self):
        '一键安装：包含安装与参数配置'
        self.install()
        self.__auto_config()
        cmd = 'systemctl restart httpd'
        os.system(cmd)

    def display(self):

        while True:
            string = '''
            ***************************

                   phpMyAdmin 配置

            ***************************

                1.安装 phpMyAdmin；
                2.手动修改 phpMyAdmin 参数配置；
                3.卸载 phpMyAdmin；
                9.一键安装配置 phpMyAdmin；
                0.返回上一页；
            '''
            print string
            flag = raw_input('请选择：')
            if flag == '1':
                self.install()
            elif flag == '2':
                self.attr_config()
            elif flag == '3':
                flag = raw_input('是否确定要卸载 phpMyAdmin[y/n]？')
                if flag == 'y':
                    self.remove()
            elif flag == '9':
                self.one_key()
            elif flag == '0' or flag == '':
                break
            else:
                print '请输入正确的序号'

class PORT():

    def list_port(self):

        cmd = 'firewall-cmd --zone=public --list-ports'
        os.system(cmd)

    def open_port(self, port):

        cmd = 'firewall-cmd --zone=public --add-port={}/tcp --permanent'.format(port)
        os.system(cmd)
        cmd = 'firewall-cmd --zone=public --add-port={}/udp --permanent'.format(port)
        os.system(cmd)
        cmd = 'firewall-cmd --reload'
        os.system(cmd)

    def close_port(self, port):

        cmd = 'firewall-cmd --zone=public --remove-port={}/tcp --permanent'.format(port)
        os.system(cmd)
        cmd = 'firewall-cmd --zone=public --remove-port={}/udp --permanent'.format(port)
        os.system(cmd)
        cmd = 'firewall-cmd --reload'
        os.system(cmd)

    def display(self):

        while True:
            string = '''
            **********************

                    端口配置

            **********************

                1.开启防火墙端口；
                2.关闭防火墙端口；
                3.列出当前已开启端口；
                0.返回上一页；
            '''
            print string
            flag = raw_input('请选择：')
            if flag == '1':
                port = raw_input('请输入要开启的端口号(批量请输入a-b这种格式)：')
                self.open_port(port)
            elif flag == '2':
                port = raw_input('请输入要关闭的端口号(批量请输入a-b这种格式)：')
                self.close_port(port)
            elif flag == '3':
                self.list_port()
            elif flag == '0' or flag == '':
                break
            else:
                print '请输入正确的序号'

class LAMP:

    def __init__(self):

        self.apache = Apache()
        self.mysql = MySQL()
        self.php = PHP()
        self.phpmyadmin = PHPMyAdmin()
        self.port = PORT()

    def get_host_ip(self):

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
     
        return ip

    def show_messages(self):

        ip = self.get_host_ip()
        print '''
        -----------------------------------------------------------

            Apache 测试路径：http://{}
            php 测试路径：http://{}/info.php
            phpMyadmin 访问路径：http://{}/phpmyadmin
            ssh 设置路径：/etc/ssh/sshd_config
            Apache 默认服务器目录：/var/www/html/
            Apache 默认参数配置目录：/etc/httpd/conf/httpd.conf

        -----------------------------------------------------------
        '''.format(ip,ip,ip)
        raw_input('请按 Enter 键继续...')

    def close_passwd_connect(self):

        filepath = '/etc/ssh/sshd_config'
        with open(filepath,'a+')as fl:
            fl.seek(0)
            data = fl.readlines()
            if 'PasswordAuthentication yes\n' in data:
                fl.seek(0)
                fl.truncate()
                for line in data:
                    if line == 'PasswordAuthentication yes\n':
                        fl.write('PasswordAuthentication no\n')
                    else:
                        fl.write(line)
                print '设置成功！你已经不能使用密码登录服务器。'
            else:
                print '无需重复设置。'
        cmd = 'service sshd restart'
        os.system(cmd)

    def apache_php_config(self):

        # 建立测试页面
        test_file = r'/var/www/html/info.php'
        if not os.path.exists(test_file):
            cmd = 'echo "<?php echo phpinfo(); ?>" >> /var/www/html/info.php'
            os.system(cmd)

        # Apache 相应配置
        # 在 apache 配置文件下增加 php5_module 和 php文件类型识别
        apache_config_file = '/etc/httpd/conf/httpd.conf'
        if os.path.exists(apache_config_file) and \
            os.path.exists('/etc/httpd/modules/libphp7.so'):
            with open(apache_config_file,'a+')as fl:
                fl.seek(0)
                data = fl.read()
                if 'LoadModule php7_module /etc/httpd/modules/libphp7.so' not in data:
                    fl.write('LoadModule php7_module /etc/httpd/modules/libphp7.so' + '\n')
                if 'AddType application/x-httpd-php .php' not in data:
                    fl.write('AddType application/x-httpd-php .php' + '\n')
                if 'AddType application/x-httpd-php-source .phps' not in data:
                    fl.write('AddType application/x-httpd-php-source .phps' + '\n')
        else:
            print '请先确认 apache 已经安装。'
        # 重启 apache 生效
        cmd = 'systemctl restart httpd'
        os.system(cmd)

    def one_key(self):

        self.mysql.one_key()
        self.apache.one_key()
        self.php.one_key()
        self.apache_php_config()
        self.phpmyadmin.one_key()
        self.show_messages()

    def display(self):

        while True:

            string = '''
                **************************

                   建站辅助脚本(centos7)

                **************************

                    1. 一键搭建 LAMP 环境
                       (Apache,MySQL5.7,PHP7.1,phpMyAdmin)
                    2. Apache 配置
                    3. MySQL  配置
                    4. PHP    配置
                    5. phpmyadmin 配置
                    6. 端口   设置
                    7. Apache 挂载 php
                    8. 显示部分重要信息
                    9. 关闭使用密码登录
                    0. 退出程序
            '''
            print(string)
            flag = raw_input('请选择：')
            if flag == '0':
                sys.exit()
            elif flag == '1':
                self.one_key()
            elif flag == '2':
                self.apache.display()
            elif flag == '3':
                self.mysql.display()
            elif flag == '4':
                self.php.display()
            elif flag == '5':
                self.phpmyadmin.display()
            elif flag == '6':
                self.port.display()
            elif flag == '7':
                self.apache_php_config()
            elif flag == '8':
                self.show_messages()
            elif flag == '9':
                flag = raw_input('你确定真的要关闭使用密码登录吗[y/n]!')
                if flag == 'y':
                    self.close_passwd_connect()
            else:
                print '请输入正确的序号。'


if __name__ == '__main__':

    try:
        lamp = LAMP()
        lamp.display()
    except KeyboardInterrupt:
        print '\n您按了终止程序按钮，现在程序退出。'
    except Exception,e:
        print e
