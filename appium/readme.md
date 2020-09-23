# 说明

使用前提前安装依赖： `pip install -r requirements.txt`

使用流程：

1. 启动`Appium`服务： 命令行为`appium` , 或者启用桌面版`Appium Desktop`客户端。
2. 启动`mitmdump` HTTP代理工具: 命令行为 `mitmdump -p 8888 -s ./flow.py` , 服务端口为8888, 监听数据使用`flow.py`处理。
3. `Android`手机(安装好mitmproxy证书) 连接到操作系统(USB或Wifi模式) 验证方法： `adb devices` 确认已经连接成功后继续。
4. 执行`Appium`模拟操作脚本: 命令为`python douyin_video.py` ，开始执行自动刷视频过程.

`douyin_video.py`脚本说明：
- 这里通过检测锁屏界面`时间`标签元素判断是否锁屏，锁屏就进行密码解锁操作，如果不需要解锁可以去掉这部分过程.
- 视频滑动分两种： 向上滑动 会直接触发视频链接API请求，向下滑动 正常操作 也会产生API调用，但是不是每次滑动都会产生,因为一次API调用会返回十几个视频地址。


