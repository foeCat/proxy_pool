# API 使用

## 接口列表

启动 ProxyPool 的 `server` 后会提供如下 HTTP 接口：

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/` | GET | 返回 API 列表 | 无 |
| `/get` | GET | 随机返回一个代理 | 可选：`?type=https` 过滤 HTTPS 能力；`?protocol=http\|socks4\|socks5` 过滤传输协议 |
| `/pop` | GET | 返回并删除一个代理 | 同 `/get` |
| `/all` | GET | 返回所有代理 | 同 `/get` |
| `/count` | GET | 返回代理数量统计 | 无 |
| `/delete` | GET | 删除指定代理 | `?proxy=host:port` 或 `?proxy=socks5://host:port` |

## 调用示例

### 在爬虫中使用

通过调用 API 接口来使用代理池：

```python
import requests


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def get_html():
    retry_count = 5
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            # 使用代理访问
            html = requests.get(
                "http://www.example.com",
                proxies={
                    "http": "http://{}".format(proxy),
                    "https": "https://{}".format(proxy),
                },
            )
            return html
        except Exception:
            retry_count -= 1
            # 删除代理池中代理
            delete_proxy(proxy)
    return None
```

本例中在本地 `127.0.0.1` 启动端口为 `5010` 的 `server`，使用 `/get` 接口获取代理，`/delete` 删除代理。

### 获取 HTTPS 代理

```python
# 只获取支持 HTTPS 的代理
proxy = requests.get("http://127.0.0.1:5010/get/?type=https").json()
```

### 获取 SOCKS 代理

```python
# 只获取 SOCKS5 代理；返回值包含 protocol 和 proxy_url
proxy = requests.get("http://127.0.0.1:5010/get/?protocol=socks5").json()
```

### 获取代理统计

```python
# 返回代理数量、HTTP 能力、传输协议和来源分布
stats = requests.get("http://127.0.0.1:5010/count/").json()
# 示例返回: {"http_type": {"http": 10, "https": 5}, "protocol": {"http": 10, "socks4": 2, "socks5": 3}, "source": {}, "count": 15}
```

## 直接读取数据库

除了通过 API 接口，也可以直接读取数据库获取代理。目前支持两种数据库：Redis 和 SSDB。

- **Redis**：存储结构为 hash，hash name 为配置项中的 `TABLE_NAME`（默认 `use_proxy`）
- **SSDB**：存储结构为 hash，hash name 为配置项中的 `TABLE_NAME`

可以在代码中自行读取数据库获取代理列表。
