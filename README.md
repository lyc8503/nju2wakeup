# 南大课表导出到 Wakeup 课表 - nju2wakeup

## 说明

如题. 就是可以导出南大课程表到 Wakeup 课表.

直接爬取南大 APP 中的课表, 应该不会出现缺漏和偏差.

## Q&A

Q: 为什么不用南哪课表? A: 功能不够多, 导入课程好像还有些小问题.

Q: 为什么不直接适配 Wakeup 课表? A: 不会 Kotlin, 而且需要多次请求 JSON, 和 Wakeup 现有架构不符.

## 使用方法

1. 下载一个 [Wakeup 课表](https://github.com/YZune/WakeupSchedule_Kotlin).

2. [Releases](https://github.com/lyc8503/nju2wakeup/releases/) 中下载运行本程序, 按照提示输入南大统一认证的用户名和密码.

   (你的用户名和密码只会被发送给南大官方.)

3. 复制程序最后的分享码, 按照提示导入课表.



