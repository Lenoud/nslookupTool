import os
import re
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, QVBoxLayout
from PyQt5.QtGui import QIcon
import random

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
        self.left = 500
        self.top = 150
        self.width = 500
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('icon.png'))

        # 创建提示文本、域名输入框、DNS输入框、查询按钮和输出框
        self.domain_label = QLabel('域名（空格分割）:', self)
        self.domain_input = QLineEdit(self)
        self.domain_input.setPlaceholderText("请输入要查询的域名或IP，例如：www.baidu.com")
        self.dns_label = QLabel('DNS（选填）:', self)
        self.dns_input = QLineEdit("8.8.8.8", self)
        self.dns_input.setPlaceholderText("请输入DNS服务器的IP地址，例如：8.8.8.8")
        self.query_button = QPushButton('查询', self)
        self.output_box = QTextEdit(self)
        self.output_box.setStyleSheet("font-size: 14px;")

        # 创建垂直布局
        layout = QVBoxLayout()
        layout.addWidget(self.domain_label)
        layout.addWidget(self.domain_input)
        layout.addWidget(self.dns_label)
        layout.addWidget(self.dns_input)
        layout.addWidget(self.query_button)
        layout.addWidget(self.output_box)

        # 设置窗口的主布局为垂直布局
        self.setLayout(layout)

        # 绑定查询按钮事件
        self.query_button.clicked.connect(self.query)

        # 绑定回车查询
        self.domain_input.returnPressed.connect(self.query)

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

            # 解析出所有IPv4地址
            ipv4_addresses = re.findall(ip_pattern, info)

            # 解析出所有IPv6地址
            ipv6_addresses = re.findall(r"[0-9a-fA-F:]+:[0-9a-fA-F:]+", info)
            has_ipv6 = bool(ipv6_addresses)

            # 提取名称
            name_match = re.search(r"名称:\s*(.*?)\n", info)
            name = name_match.group(1).strip() if name_match else ""

            # 提取别名
            alias_match = re.findall(r"Aliases:\s*(.*(?:\n\s+.*)*)", info)
            aliases = [alias.strip() for alias in re.findall(r"\S+", alias_match[0])] if alias_match else []
            has_alias = bool(aliases)

            # 添加到输出文本
            output_text += f"域名：{domain}\n"
            output_text += f"使用DNS：{dns}\n\n"
            output_text += f"名称：\n{name}\n\n"
            output_text += "IPv4地址：\n"
            if dns == '':
                output_text += "\n".join(ipv4_addresses)
            else:
                output_text += "\n".join(ipv4_addresses[1:])
            output_text += "\n\n"

            if has_ipv6:
                output_text += "IPv6地址：\n"
                output_text += "\n".join(ipv6_addresses) + "\n\n"

            if has_alias:
                output_text += "别名：\n"
                output_text += "\n".join(aliases) + "\n\n"

            # # 执行ping测试
            # if (platform.system() == 'Windows'):
            #     ping = subprocess.Popen(
            #         'ping -n 1 {}'.format(domain),
            #         shell=False,
            #         close_fds=True,
            #         stdout=subprocess.PIPE,
            #         stderr=subprocess.PIPE
            #     )
            # else:
            #     ping = subprocess.Popen(
            #         'ping -c 1 {}'.format(domain),
            #         shell=False,
            #         close_fds=True,
            #         stdout=subprocess.PIPE,
            #         stderr=subprocess.PIPE
            #     )
            # try:
            #     out, err = ping.communicate(timeout=8)
            #     if 'ttl' in out.decode('GBK').lower():
            #         output_text += "域名可达！(可以ping通)\n" + "+" * 60
            #     else:
            #         output_text += "域名不可达！(无法ping)\n" + "+" * 60
            # except:
            #     output_text += "域名不可达！(无法ping)\n" + "+" * 60
            # ping.kill()

            # 查询结束分割数据
            output_text += "\n" + "=" * 30 + "\n"

        # 在输出框中显示结果
        self.output_box.setText(output_text)
        # 闪烁查询按钮
        # 生成随机颜色值，排除黑色
        color = "#{:06x}".format(random.randint(0x000001, 0xFFFFFF))
        # 设置查询按钮的样式
        self.query_button.setStyleSheet(f"background-color: {color}")
        self.query_button.repaint()
        QApplication.processEvents()


if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    app.exec_()
