# AutoChatScript

[English](readme.md) | [中文](readme_cn.md)

AutoChatScript is an automation script implemented using the PyAutoGUI library, aimed at automating chat with ChatGPT(website). This project relies entirely on reading and using the mouse, keyboard, and screen without reverse-engineering any web requests or needing to install browser plugins.

## Features

- **Automated Initialization**: Automatically initializes the script, no manual screenshotting required.
- **Cross-Platform Support**: Future support for platforms beyond Windows.
- **Full Operation Support**: Supports a series of operations including creating new dialogues, submitting, regenerating, modifying, etc.
- **Support for More Websites**: This project is not only for ChatGPT but will support more chat websites in the future.

## Installation Guide

Before starting, ensure you have Python 3.6 or higher installed on your computer.

1. **Clone the Repository**

   First, clone the project repository to your local computer:

   ```
   git clone https://github.com/MaoXiaoYuZ/AutoChatScript.git
   cd AutoChatScript
   ```

2. **Install Dependencies**

   Use pip to install the required Python libraries:

   ```
   pip install -r requirements.txt
   ```

## Usage Instructions

Before running the script, make sure you have opened the web version of ChatGPT and logged into your account.

1. **Start Demo**

   ```
   python demo.py
   ```

   Below is a demonstration of the demo running:

   ![Chat with ChatGPT](assets/chat_with_chatgpt.gif "Demo running live")

   The demo will initialize certain features when needed, shown below is the process of automatically initializing the submit button after running demo.py.

   ![Init Submit Button](assets/init_submit_button.gif "Initialize Submit Button")

   Below is the initialization process for the resubmit button the first time the rewrite submit feature is used.

   ![Init ReSubmit Button](assets/init_resubmit_button.gif "Initialize Resubmit Button")

2. **Provide OpenAI Format API**

   ```
   python openai_api.py
   ```

## Precautions

- This project currently only supports the Windows operating system.
- Ensure that the ChatGPT web version is already open on your screen before running the script.
- As page layout updates may affect script operation, please check the project repository regularly for updates.

## Contributions

We welcome any form of contribution, whether feature requests, bug reports, or code submissions. Please submit your contributions through the GitHub repository's Issues and Pull Requests.
