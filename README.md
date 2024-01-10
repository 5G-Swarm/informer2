# informer2

## 安装方法
```bash
git clone git@github.com:5G-Swarm/informer2.git
cd informer2
pip install -e .
```

## 使用方法
#### 写一个config.yaml文件：
```
debug_mode: False
use_log: True
robot_id: 0

role_info:
    is_client: False # 如果你是边缘服务器就是False，如果是机器人就是True
    id: 'vehicle-01'

network_info:
    ip: '127.0.0.1'

    target_info:
        ip: '172.16.10.3' # 如果你是边缘服务器就是127.0.0.1，如果是机器人就是边缘服务器的IP

message_info:
    img: # 你要发的消息的key
        is_tcp: True
        port: 10000 # 你要发的消息的端口，建议xx000这样写
        width: 640
        height: 480
    cmd:
        is_tcp: True
        port: 11000
```

#### 假设你是边缘服务器
```python
from informer import Informer
# 创建一个通讯的类，注意消息的key不要改，必须是xxx_recv或者send_xxx，否则找不到对应的函数
class Server(Informer):
    def img_recv(self):
        self.recv('img', parse_img)

    def send_cmd(self, message):
        self.send(message, 'cmd')

# 写下回调函数，robot_id用来区分是哪个ID发回来的
def parse_img(message, robot_id):
    global global_img_dict
    print("Get img size:",len(message), 'from id', robot_id)
    nparr = np.frombuffer(message, np.uint8)
    global_img_dict[robot_id] = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)

# 创建20个通讯实例，ID分别是从0到19，回调函数中就可能收到ID是0~19
ifm_list = [
    Server(
    config = 'config_recv.yaml',
    robot_id = item
    )
    for item in range(20)
]

# 向某个ID实例发送数据，send_xxx()中的数据必须是二进制
cmd = cmd_msgs_pb2.Cmd()
cmd.v = 1.0
cmd.w = 1.0
sent_data = cmd.SerializeToString()

ifm_list[5].send_cmd(cmd)
```
#### 假设你是机器人
```python
from informer import Informer

class Client(Informer):
    def send_img(self, message):
        self.send(message, 'img')

    def cmd_recv(self):
        self.recv('cmd', parse_cmd)

# 创建1个通讯实例
ifm = Client(
    config = 'config.yaml',
    robot_id = 5, # 可以程序里给定一个ID，如果不写就是yaml里的ID
    )
# 其他写法和边缘端完全一致
# 如果要中转数据，就创2个通讯实例，互相传递消息，见https://github.com/5G-Swarm/ros-edge-transfer/blob/main/scripts/edge-vehicle.py
```
