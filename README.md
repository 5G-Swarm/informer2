# informer2

### 特性

* 创建tcp连接不会阻塞主线程，因为开线程去创tcp连接
* 创 tcp client主动连接失败会反复尝试连接
* tcp连接未创建的情况下（对方接收端程序没启动）发送数据，会每隔一秒报错一次，但是会循环等待

