# sht自动签到评论脚本

这是一个用于 sht 论坛的自动签到和评论脚本，支持多账号管理。

## 功能特点

- 支持多账号自动签到
- 支持多账号自动评论
- 支持代理配置
- 支持青龙面板通知


## 环境变量配置

必需的环境变量：
- `FETCH_98TANG_1`, `FETCH_98TANG_2`, ... - 用于存储不同账号的登录凭证
  - 格式为网站的 fetch 请求格式
  - 可以配置多个账号，按数字递增

可选的环境变量：
- `DEAULT_PROXY_1`, `DEAULT_PROXY_2`, ... - 代理配置
  - 格式如：`http://user:pass@host:port` 或 `socks5://host:port`

## fetch获取说明
1. [点击这里](https://www.sehuatang.net/plugin.php?id=dd_sign&view=daysign)
2. *F12*进入**开发者模式**
3. 选择**网络**标签
4. *Ctrl+R*刷新页面，右键复制**Copy as cURL** 或者 **Copy as Node.js fetch**

## 通知说明
本脚本默认使用青龙系统通知，如通知出现问题，请自行检查系统通知渠道
  

## 青龙面板配置

1. 依赖安装：
   - 进入青龙面板 -> 依赖管理
   - 切换到 "Python" 分类
   - 点击 "添加依赖"
   - 分别添加：httpx、beautifulsoup4、flaresolverr

2. 环境变量配置：
   - 进入青龙面板 -> 环境变量
   - 添加必需的环境变量

3. 定时任务配置：
   - 进入青龙面板 -> 定时任务
   - 添加两个任务：
     ```
     名称: 每日签到
     命令: python3 daysignMulti.py
     定时: 随机时间，如 30 8 * * *（每天8:30执行）
     
     名称: 每日评论
     命令: python3 dayCommentMulti.py
     定时: 随机时间，如 30 9,10 * * *（每天9:30 10:30执行）
     ```

## 订阅方式

1. 在青龙面板中添加订阅：
   ```
   名称: sht自动签到评论
   类型: 公开仓库
   链接: https://github.com/danndee1/shtdaysign.git
   定时规则: 0 0 * * *
   ```

2. 订阅后会自动创建定时任务，请根据实际情况修改执行时间。

## 注意事项

1. 请确保环境变量配置正确
2. 建议两个脚本的执行时间错开
3. 如果遇到 Cloudflare 验证，需要配置 FlareSolverr 服务
4. 确保青龙面板的通知功能已正确配置 
