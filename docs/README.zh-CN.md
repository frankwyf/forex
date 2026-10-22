# Forex Local Visual

Django 外汇、黄金与比特币行情采集及可视化项目。0.2.0 支持离线合成数据演示、完整批次校验、事务替换和跨平台自动测试。

## 本地体验

使用 Python 3.12 和仓库内 .venv；macOS 用户先执行[外置 SSD 配置](macos-development.md)，再按[主 README](../README.md)安装依赖。Windows PowerShell 的步骤也保留在主 README。

为演示指定一个新的独立 SQLite 文件，执行 migrate 和 seed_demo，再运行本地开发服务器。演示数据全为合成数据；已有市场记录时命令会拒绝写入。两张图表页面分别位于 /visual/history/ 和 /visual/recent/。

执行 python scripts/verify.py 可完成配置、迁移检查和离线测试。验证过程忽略本地 .env，并使用临时隔离数据库。此 Mac 的 TMPDIR 必须在外置盘。

## 深入阅读

- [数据契约与架构](architecture.md)
- [详细升级路线与验收标准](roadmap.zh-CN.md)
- [贡献指南](../CONTRIBUTING.md)、[安全报告](../SECURITY.md)
- [0.2.0 发布说明](releases/v0.2.0.md)、[发布流程](releasing.md)

项目当前用于本地研究和学习。自动化演示与测试不会访问 Yahoo，也不会启动采集服务。代码采用 MIT 协议；真实行情数据受来源条款约束，不随发布包分发。
