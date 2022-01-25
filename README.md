<div align="center">
    <img width="" src="docs\img\mkhmv10ot7161.png" alt="logo"></br>
    <h1>ALICE·SYNTHESIS·THIRTY</h1>
</div>

---

<div align="center">
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg"/>
    <h3>新一代基于 Graia 生态的动态机器人终端</h3>
    <div>ALICE·SYNTHESIS·THIRTY之名取自动漫《刀剑神域》中的角色 <a href="https://zh.moegirl.org.cn/%E7%88%B1%E4%B8%BD%E4%B8%9D%C2%B7%E6%BB%8B%E8%B4%9D%E9%B2%81%E5%BA%93">爱丽丝·滋贝鲁库</a></div>
    <br>
    <div>若您在使用过程中发现了**bug**或有一些建议，欢迎提出ISSUE或PR</div>
    <br>
</div>

## 目录

* [目录](#目录)
* [项目特色](#项目特色)
* [开始使用](#开始使用)
  + [使用前准备](#使用前准备)
  + [如何启动](#如何启动)
  + [参数说明](#参数说明)
    - [config.yaml](#configyaml)
* [使用文档](#使用文档)
* [注意](#注意)
* [TODO](#todo)
* [鸣谢](#鸣谢)

## 项目特色

- 完备的权鉴系统
- 冷却与频率限制
- 在线调试
- 事件适配器
- 真SSH终端
- FTP
- Github
- 持久化
- 模块间易解耦
- API易拓展
- 注册定时任务
- 内置Playwirght

## 开始使用

### 使用前准备

- 下载 [mirai-console](https://github.com/mamoe/mirai-console) 并配置 [mirai-api-http](https://github.com/project-mirai/mirai-api-http) ，这些都可以在 [mirai](https://github.com/mamoe/mirai) 项目中找到
- 若上一条不会配置，请考虑使用 [mirai-console-loader](https://github.com/iTXTech/mirai-console-loader) 加载器进行配置
- 打开 `config.yaml`，配置好个人信息，配置说明见[config文件参数说明](#configyaml)

### 如何启动

首先，启动 mirai-console，确保其正常运行且插件正常安装
在文件夹下执行 `python main.py` 即可

### 参数说明

#### config.yaml

用于存储机器人的各种配置

| 参数名                | 说明                         |
| --------------------- | ---------------------------- |
| Alice                 | Graia for mirai 内核         |
| BotSession.host       | mirai-api-http host          |
| BotSession.account    | bot 账户                     |
| BotSession.verify_key | mirai-api-http 的 verify_key |
| SSH.host              | SSH IP地址                   |
| SSH.port              | SSH 端口                     |
| SSH.username          | SSH 登录用户名               |
| SSH.password          | SSH 登录密码                 |

## 使用文档
 
完善中

## 注意

- 目前不适合直接部署, 建议文档完善后再部署

## TODO

* [ ] 完善文档
* [ ] 命令宏

## 鸣谢

- [mirai](https://github.com/mamoe/mirai) ，高效率 QQ 机器人框架 / High-performance bot framework for Tencent QQ
- [mirai-api-http](https://github.com/project-mirai/mirai-api-http) ，Mirai HTTP API (console) plugin
- [Graia Ariadne（目前使用）](https://github.com/GraiaProject/Ariadne) ，一个优雅且完备的 Python QQ 自动化框架。基于 Mirai API HTTP v2。
- [Graia Appliation（老版使用）](https://github.com/GraiaProject/Application) ，一个设计精巧, 协议实现完备的, 基于 mirai-api-http 的即时聊天软件自动化框架.
