# AutoChatScript

[English](readme.md) | [中文](readme_cn.md) | [日本語](readme_jp.md)

AutoChatScript是一个使用PyAutoGUI库实现的自动化脚本，旨在自动化与ChatGPT网页的对话。该项目完全依靠读取和使用鼠标，键盘，屏幕，不逆向任何网页请求，也不需要安装浏览器插件。

## 特性

- **自动化初始化**：自动初始化脚本，无需人为截图。
- **全平台支持**：后续支持除Windows外更多平台。
- **全操作支持**：支持新建对话，提交，重新生成，修改等一系列操作。
- **支持更多网站**：本项目不仅仅针对ChatGPT，后续将支持更多Chat网站。

## 安装指南

在开始之前，请确保您的计算机上已安装 Python 3.6 或更高版本。

1. **克隆仓库**

    首先，克隆该项目仓库到您的本地计算机：

    ```
    git clone https://github.com/MaoXiaoYuZ/AutoChatScript.git
    cd AutoChatScript
    ```

2. **安装依赖**

    使用 pip 安装所需的 Python 库：

    ```
    pip install -r requirements.txt
    ```

## 使用说明

在运行脚本前，请确保您已经打开了ChatGPT网页版，并登录到您的账户。

1. **启动Demo**

    ```
    python demo.py
    ```

    下面展示是demo的运行实况:

    ![chat_with_chatgpt](assets/chat_with_chatgpt.gif "Demo的运行实况")

    该demo会再需要用到某项功能时对该功能进行初始化，下面展示的是运行demo.py后程序自动初始化提交按钮的过程。

    ![Init Submit Button](assets/init_submit_button.gif "初始化提交按钮")

    下面展示的是第一次使用重写提交功能是，初始化重写提交按钮的过程。

    ![Init reSubmit Button](assets/init_resubmit_button.gif "初始化重新提交按钮")

2. **提供openai格式api**


    ```
    python openai_api.py --server-port 8000
    ```

## 注意事项

- 该项目目前仅支持 Windows 操作系统。
- 确保在运行脚本之前，您的屏幕上已经打开了ChatGPT的网页版。
- 由于页面布局的更新可能会影响脚本的运行，请定期检查项目仓库以获取更新。

## 贡献

我们欢迎任何形式的贡献，无论是功能请求、bug 报告还是代码提交。请通过 GitHub 仓库的 Issues 和 Pull Requests 来提交您的贡献。
