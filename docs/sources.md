# 知识来源与蒸馏溯源清单

> 本文档记录课程知识内容的来源与逐课溯源映射：每个技术事实来自哪里、在哪一课被使用。
> 所有来源均为课程制作期间实际对照的权威材料；本清单由课程正文各课"延伸阅读"块与《课程计划》各课"参考资料"字段汇总而成，可逐条回查。

## 一、蒸馏方法

课程知识内容蒸馏自权威来源，路径分四步：

1. **教材定框架**——9 阶段 30 课时的自顶向下骨架，对齐主干教材《计算机网络：自顶向下方法》（Kurose & Ross，第 8 版）的章节顺序与知识主线；
2. **一手标准定事实**——协议字段、状态机、术语以 RFC / IEEE 标准原文为准。制作期对阶段 4–7 的 16 处教材引用做过对照官方目录的审计（见 [CHANGELOG.md](../CHANGELOG.md) 0.5 条目）；本清单编制时，全部课时的章节引用又对照官方 8E 目录逐条复核，修正了 7 处编号偏差（明细记录于 CHANGELOG）；两轮全课程审查均设"协议标准与 RFC 一致性"维度；
3. **官方实验定动手环节**——实验数据取自 Kurose 官方 Wireshark Labs 的脱敏 trace 与 Cisco Packet Tracer 仿真，不碰真实流量；
4. **教学结构重设计**——问题驱动的七节课时结构、阶段项目、结业考试为原创组织。

一句话概括：**取材的取舍——教材的百科式广度被压缩，保留并强化了可动手验证的主线。**

## 二、来源总表

| 类型 | 来源 | 在课程中的角色 |
|---|---|---|
| 主干教材 | Kurose & Ross《计算机网络：自顶向下方法》第 8 版 | 全课程知识骨架；30 个课时中 29 课标注对应章节（21 课标注于课程"延伸阅读"块，其余出自课程计划"参考资料"字段） |
| 参考书 | 《TCP/IP 详解 卷1：协议》 | 课时 29：协议行为的第一性来源（排障考试对照） |
| IETF 标准 | RFC 791 / 8200 / 826 / 894 / 950 / 1918 / 2606 / 2663 / 3021 / 5737 / 7465 / 8446 / 9110 / 9112 / 9114 / 9293，共 16 份（RFC 793 作为被 9293 取代的历史标准提及） | 协议事实基准 |
| IEEE 标准 | 802.11（无线）、802.1Q / 802.1D（VLAN 与 STP） | 无线与交换章节的标准出处 |
| 安全标准 | NIST SP 800-115（安全测试技术指南）、等保 2.0（GB/T 22239） | 授权扫描方法论（课时 26）、安全架构框架（课时 27） |
| 官方实验体系 | Kurose & Ross Wireshark Labs（v8.1 / v9.0）及官方脱敏 trace | 各阶段动手环节的数据来源 |
| 工具官方文档 | Wireshark、Cisco Packet Tracer、Cisco IOS 命令参考、nmap、iperf3、OpenSSL、Python cryptography、Linux tc/netem | 实验命令与参数依据 |
| 行业组织文档 | Wi-Fi Alliance（WPA3 / SAE） | 无线安全演进（课时 22） |
| 进阶路标 | Stanford CS144 等深入方向入口 | 结业回顾（课时 30） |

## 三、30 课时逐课溯源映射

> 章节/编号均摘自课程正文各课"延伸阅读"块（`index.html`）与课程计划各课"参考资料"字段（`docs/course-plan.md`）。

| 课时 | 主干教材（Kurose & Ross 8E） | RFC / 标准 | 官方实验与工具文档 |
|---|---|---|---|
| 01 摸底与环境 | 第 1 章前言（作业阅读） | — | Wireshark Labs 官方指南；Packet Tracer（Cisco NetAcad）；Python 3 |
| 02 浏览器输入网址后发生了什么 | 第 1 章 | — | Wireshark Getting Started Lab；HTTP 明文测试页 |
| 03 数据封装与网络身份 | 第 1.5 节（协议层次与封装） | — | — |
| 04 HTTP 协议 | 第 2.2 节 | RFC 9110 | Wireshark HTTP Lab |
| 05 HTTPS 与 HTTP 的区别 | 第 8.6 节（Securing TCP Connections，安全章） | RFC 8446；RFC 9110-9114 系列 | — |
| 06 DNS 域名解析 | 第 2.4 节（DNS） | — | Wireshark DNS Lab |
| 07 DHCP 与邮件协议 | 第 2.3 节（电子邮件）；DHCP 见第 4.3.2 节 | — | Wireshark DHCP Lab；MailHog（本地测试） |
| 08 TCP 三次握手与四次挥手 | 第 3.5 节 | RFC 9293 | Wireshark TCP Lab |
| 09 TCP 可靠传输机制 | 第 3.5.3–3.5.4 节 | RFC 9293 | — |
| 10 TCP 流量控制与拥塞控制 | 第 3.5.5 节（流量控制）、第 3.6–3.7 节（拥塞控制） | — | iperf3（iperf.fr）；Linux tc / netem |
| 11 Socket 编程实战 | 第 2.7 节（Socket 编程，2.7.1 UDP / 2.7.2 TCP） | RFC 9112 | Python socket 官方文档 |
| 12 IP 协议 | 第 4.3 节 | RFC 791；RFC 8200；RFC 1918 | Wireshark IP Lab |
| 13 子网划分与 CIDR | 第 4.3.2 节 | RFC 950；RFC 3021 | Subnet Calculator（验证手算） |
| 14 路由原理 | 第 4.2、5.2–5.4 节 | — | Cisco 静态路由官方文档；PT 官方教程（Routing Basics） |
| 15 NAT 与 ICMP | 第 4.3.3 节 | RFC 2663 | Wireshark NAT / ICMP Lab |
| 16 企业网络仿真（项目） | 第 4–5 章（4.1–4.3 / 5.2 / 5.6 重读） | RFC 5737 | Packet Tracer 官方教程 |
| 17 以太网与帧结构 | 第 6.1、6.3.2、6.4.2 节 | RFC 894 | Wireshark Ethernet/ARP Lab（v8.1/v9.0） |
| 18 ARP 协议 | 第 6.4.1 节 | RFC 826 | Wireshark Ethernet/ARP Lab（同上） |
| 19 交换机与 VLAN | 第 6.4.3–6.4.4、6.6 节 | IEEE 802.1Q / 802.1D | PT 官方教程（VLAN 章节） |
| 20 局域网综合抓包（项目） | 第 6 章（6.3–6.6 重读） | — | PT 官方教程（Simulation 模式）；Wireshark 官方 trace 库 |
| 21 802.11 无线局域网 | 第 7.3 节 | IEEE 802.11 | Wireshark 802.11 WiFi Lab（v8.1/v9.0） |
| 22 无线安全 | 第 8.8 节 | RFC 7465；IEEE 802.11 | Wi-Fi Alliance（WPA3/SAE）；同上 WiFi Lab |
| 23 网络性能与基础排障 | 第 1.4 节（时延与吞吐） | — | iperf3（iperf.fr） |
| 24 密码学基础 | 第 8.2–8.4 节 | — | Python cryptography（cryptography.io）；OpenSSL |
| 25 TLS 协议 | 第 8.6 节 | RFC 8446 | Wireshark TLS Lab |
| 26 主机防火墙与授权扫描 | 第 8.9 节 | NIST SP 800-115 | nmap（nmap.org/book） |
| 27 安全架构概览 | 第 8 章（8.7 IPsec/VPN）；第 5.5 节（SDN） | 等保 2.0（GB/T 22239） | — |
| 28 安全网络架构（项目） | 第 8 章（8.2–8.4 / 8.6 / 8.7 / 8.9） | RFC 5737；RFC 2606 | Packet Tracer 官方教程 |
| 29 故障定位实战考试 | — | — | 《TCP/IP 详解 卷1：协议》；Cisco IOS 命令参考；Wireshark 官方文档 |
| 30 口述答辩与课程复盘 | 第 8 版结业书单（按薄弱点分章回读） | — | Stanford CS144 等进阶入口 |

## 四、证据链索引

除引用本身外，制作与维护过程留有以下可查证痕迹：

| 证据 | 位置 | 说明 |
|---|---|---|
| 全书引用审计 | [CHANGELOG.md](../CHANGELOG.md) 0.5 条目 | 制作期将阶段 4–7 的 16 处教材引用点逐一对照 Kurose 8E 官方目录核对一致 |
| 协议标准审查维度 | [docs/reviews/](reviews/) 两轮审查报告 | 两轮全课程审查均含"协议标准（与 RFC 一致性）"维度，逐项磁盘取证 |
| RFC 对照修复实例 | CHANGELOG v1.1 修复 #2 | 审查发现 TCP 头部保留位与 RFC 9293 不符后，对照原文修正（保留 3 位 + 9 标志位）；`git diff v1.0 v1.1 -- index.html` 可直接验证 |
| 原始引用位置 | `index.html` 各课"延伸阅读"块 | 本清单第三节的每一行，均可在对应课时的"延伸阅读"块或课程计划的"参考资料"字段中找到原文 |
