# 隐私优先代理池

这部分不改变原有 `use_proxy`。它从当前池动态读取代理，把通过隐私检查的记录写入独立 Redis hash `privacy_proxy`。

## 回显服务

在云主机上运行：

```bash
ECHO_SECRET='generate-a-long-random-secret' ECHO_PORT=8088 \
  python3 privacy_echo.py
```

生产环境优先使用直连 HTTPS（固定证书/域名），这样应用看到的 `client_ip` 就是代理的 TCP 对端。若放在反向代理后，必须使用可信的 PROXY protocol 或受控的来源头，否则回显到的会是反向代理 IP。回显服务没有 UI，也不会记录请求日志。

## 本地检查

在代理池项目目录运行：

```bash
ECHO_URL_TEMPLATE='https://cloud.example/p/{nonce}' \
ECHO_SECRET='same-secret-as-echo' \
PRIVACY_WORKERS=64 \
./run_privacy_check.sh
```

检查条件：响应成功、nonce/HMAC 正确、出口 IP 不等于直连基线 IP，且回显头中不包含直连基线 IP。出口 IP 重复时只保留一条入口。

只有 SOCKS5/SOCKS5H 会写入 `privacy_proxy`；HTTP 和 SOCKS4 会被跳过。远端 DNS
成功的 SOCKS5H 记录优先级为 100，本地 DNS 的 SOCKS5 为 50。相同 `exit_ip`
只保留优先级更高的入口，因此 API 默认总是先返回 SOCKS5H。

如果本轮没有任何通过项，脚本保留上一轮 `privacy_proxy`，避免云端故障把可调用池清空。

## API

复用同一项目启动一个独立实例即可：

```bash
PORT=5010 TABLE_NAME=privacy_proxy DB_CONN='redis://@proxy-pool-jhao104-redis:6379/0' \
  python3 proxyPool.py server
```

宿主映射到 `5012:5010` 后，调用 `http://127.0.0.1:5012/get/`；也可用
`?protocol=socks5h` 或 `?protocol=socks5` 指定协议。现有 `5011` API 和
`use_proxy` 不受影响。该实例只有 API，没有 Web UI；当前尚未启动，需先完成回显
端点配置。

## 定时

等回显端点验收后，再安装并启用独立 systemd timer（当前模板为 20 分钟一轮）：

```bash
sudo install -m 0644 deploy/privacy-check.service deploy/privacy-check.timer /etc/systemd/system/
sudo install -d -m 0750 /etc/default
sudoedit /etc/default/proxy-pool-jhao104-privacy  # 填 ECHO_URL_TEMPLATE/ECHO_SECRET/DB_CONN
sudo systemctl daemon-reload
sudo systemctl enable --now privacy-check.timer
```

不要把它并入现有 fetch/check timer。回滚时只需 `systemctl disable --now privacy-check.timer`
并停止/删除 `proxy-pool-jhao104-privacy` 容器；`use_proxy`、5011 和原 scheduler 不受影响。
