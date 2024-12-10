# ARL-Finger-ADD

ARL-Finger-ADD 是一个用于批量添加指纹到`ARL(最新版)`的工具。利用ARL提供一个简单易用的接口，使用户可以轻松地管理和增强ARL中的指纹库。
看网上别人的都是一个一个添加太慢了，这里多进程+多线程操作，并且收集了一些网上的finger.json.

## 特性

- **批量添加**：支持从本地文件批量导入指纹数据至ARL。
- **预置指纹库**：提供的超过20,000个预定义指纹。
- **高效处理**：添加指纹时采用多进程+多线程操作，显著提高处理速度和效率。
- **管理功能**：除了添加指纹外，还支持一键删除所有已添加的指纹，便于维护和清理。

## 使用方法

### 安装依赖
使用前先安装requests模块
```bash
pip3 install requests
```

### 添加指纹
默认使用json_path 中的指纹
```bash
python3 ARl-Finger-ADD.py https://192.168.1.1:5003/ admin password 
```
如果你有新的指纹，在后面添加路径即可
```
python3 ARl-Finger-ADD.py https://192.168.1.1:5003/ admin password  xxx/xx/xxx
```
### 删除指纹
```bash
python3 ARL-Finger-DELETE.py <login_name> <login_password> <login_url>
```
