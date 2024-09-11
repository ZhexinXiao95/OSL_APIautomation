# Automation API Test

1. RFQ trade
2. Exchange trade

## 

- [安装](#安装)
- [使用方法](#使用方法)
- [API文档](#API文档)

## 安装
详情见requirements.txt

## 使用方法
已隐藏，pytest.ini文件，相关环境变量以及配置文件，找Shawn获取


## pytest框架测试 已完成功能

RFQ

Exchange

## Function API已实现功能

OPS Deposit

运行代码：

OPS_API().ops_authToken()

OPS_operation().account_deposit('HKD',100,'shawn.xiao@osl.com')


## API文档
https://osl.com/reference/cancel-orders
```bash
# 克隆项目
git clone https://gitlab.com/_bcgroup/qa/api-test-sz.git

# 进入项目目录
cd yourproject

# 安装依赖
pip install -r requirements.txt

