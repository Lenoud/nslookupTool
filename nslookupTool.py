import os
import re
import platform
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
from PyQt5.QtGui import QIcon



def validate_dns(dns):
    # 使用正则表达式验证IP地址格式
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    if re.match(pattern, dns):
        return True
    else:
        return False


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = '域名解析查询'
        self.left = 100
        self.top = 100
        self.width = 500
        self.height = 500
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('icon.png'))

        # 创建提示文本、域名输入框、DNS输入框、查询按钮和输出框
        self.domain_label = QLabel('域名（空格分割）:', self)
        self.domain_label.move(10, 5)
        self.domain_input = QLineEdit(self)
        self.domain_input.move(30, 20)
        self.domain_input.resize(200, 30)
        self.dns_label = QLabel('DNS（选填）:', self)
        self.dns_label.move(250, 5)
        self.dns_input = QLineEdit(self)
        self.dns_input.move(320, 20)
        self.dns_input.resize(160, 30)
        self.dns_input.setText('8.8.8.8')
        self.query_button = QPushButton('查询', self)
        self.query_button.move(420, 70)
        self.query_button.resize(60, 30)
        self.output_box = QTextEdit(self)
        self.output_box.move(20, 110)
        self.output_box.resize(460, 360)

        # 绑定查询按钮事件
        self.query_button.clicked.connect(self.query)

        self.show()

    def query(self):
        # 获取输入的域名和DNS
        domain_input = self.domain_input.text()
        dns = self.dns_input.text()



        if dns and not validate_dns(dns):
            QMessageBox.warning(self, '提示', 'DNS格式不正确！')
            return

        domains = domain_input.split()
        output_text = ""

        for domain in domains:
            # 执行nslookup查询
            ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
            info = os.popen(f"nslookup {domain} {dns}").read()

            # 解析出所有IP地址
            ips = re.findall(ip_pattern, info)


            # 输出所使用的DNS和解析出的所有IP地址
            output_text += f"域名：{domain}\n"
            output_text += f"使用DNS：{dns}\n\n"
            output_text += "IP地址：\n"
            if dns == '':
                output_text += "\n".join(ips)
            else:
                output_text += "\n".join(ips[1:])
            output_text += "\n\n"

            # 执行ping测试
            if (platform.system() == 'Windows'):
                ping = subprocess.Popen(
                    'ping -n 1 {}'.format(domain),
                    shell=False,
                    close_fds=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                ping = subprocess.Popen(
                    'ping -c 1 {}'.format(domain),
                    shell=False,
                    close_fds=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            try:
                out, err = ping.communicate(timeout=8)
                if 'ttl' in out.decode('GBK').lower():
                    output_text += "域名可达！\n"+"+"*60
                else:
                    output_text += "域名不可达！\n"+"+"*60
            except:
                output_text += "域名不可达！\n"+"+"*60
            ping.kill()

            output_text += "\n\n"

        # 在输出框中显示结果
        self.output_box.setText(output_text)


if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    app.exec_()
