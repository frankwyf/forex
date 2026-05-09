# Forex Local Visual（中文）

语言: [English](README.en.md) | 中文 | [日本語](README.ja.md)

## 项目简介

Forex Local Visual 是一个基于 Django 的开源项目，用于采集并可视化外汇、大宗商品和加密货币数据。

## 功能特性

- 使用 APScheduler 进行定时数据采集
- 通过 Django ORM + SQLite 存储数据
- 使用 pyecharts 进行交互式图表展示
- 采用可扩展的应用结构，便于二次开发

## 快速开始

1. 创建并激活虚拟环境。

```powershell
cd forex\forex
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. 安装依赖。

```powershell
pip install -r requirements.txt
```

3. 配置环境变量。

```powershell
Copy-Item .env.example .env
```

请设置 DJANGO_SECRET_KEY、DJANGO_DEBUG、DJANGO_ALLOWED_HOSTS。

4. 初始化数据库并启动。

```powershell
python manage.py migrate
python manage.py runserver
```

访问: http://127.0.0.1:8000/visual/

## 贡献指南

1. Fork 本仓库。
2. 新建功能分支。
3. 推送前执行检查。
4. 提交 Pull Request 并描述变更背景。

## 安全说明

不要提交 .env、本地数据库、日志文件和采集生成的 CSV 数据。

## 许可证

项目采用 MIT 协议，详见 ../LICENSE。
