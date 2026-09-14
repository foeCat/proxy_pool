# 免费代理源清单 — 实测有贡献的源（2026-09-14）

- 快照时间：2026-09-14 14:10（本地）
- 口径：把 **241 条经本机实测存活** 的代理，逐个回溯到它在 `work/<shard>/` 里被哪个源的文件收录
- 结果：**84 个源有贡献，覆盖 219/241 条可用代理**
- 说明：同一源在多个分片重复登记已按 URL 合并；代理会在多个源间互抄，故命中数之和大于 241

## Top 40（按贡献的可用代理数）

| # | 源 | 协议 | 可用数 | URL |
|---:|---|---|---:|---|
| 1 | `ErcinDedeoglu-socks5` | socks5 | **142** | https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt |
| 2 | `ErcinDedeoglu-socks4` | socks4 | **128** | https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt |
| 3 | `dpangestuw-socks5` | socks5 | **116** | https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/socks5_proxies.txt |
| 4 | `openproxylist-socks5` | socks5 | **115** | https://openproxylist.xyz/socks5.txt |
| 5 | `proxyscrape-v4-https` | https | **113** | https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=https&format |
| 6 | `openproxylist-xyz-socks5` | socks5 | **110** | https://api.openproxylist.xyz/socks5.txt |
| 7 | `openproxylist-xyz-http` | http | **103** | https://api.openproxylist.xyz/http.txt |
| 8 | `proxyspace-http` | http | **99** | https://proxyspace.pro/http.txt |
| 9 | `proxyspace-socks5` | socks5 | **96** | https://proxyspace.pro/socks5.txt |
| 10 | `openproxylist-socks4` | socks4 | **84** | https://openproxylist.xyz/socks4.txt |
| 11 | `thespeedx-socks5` | socks5 | **82** | https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt |
| 12 | `TheSpeedX-SOCKS-List-socks5` | socks5 | **82** | https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt |
| 13 | `thespeedx-http` | http | **76** | https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt |
| 14 | `proxyscrape-v4-socks5` | socks5 | **75** | https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=socks5&forma |
| 15 | `proxyscrape-v3-socks5` | socks5 | **72** | https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5 |
| 16 | `openproxylist-xyz-socks4` | socks4 | **70** | https://api.openproxylist.xyz/socks4.txt |
| 17 | `proxyspace-socks4` | socks4 | **68** | https://proxyspace.pro/socks4.txt |
| 18 | `proxyscrape-v2-https` | https | **68** | https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=10000&country=all& |
| 19 | `proxyscrape-v2-legacy-socks5` | socks5 | **66** | https://api.proxyscrape.com/?request=getproxies&protocol=socks5 |
| 20 | `thespeedx-socks4` | socks4 | **63** | https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt |
| 21 | `TheSpeedX-SOCKS-List-socks4` | socks4 | **63** | https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt |
| 22 | `proxmint-socks5` | socks5 | **58** | https://raw.githubusercontent.com/proxmint/free-proxy-list/main/proxies/socks5.txt |
| 23 | `monosans/http` | http | **57** | https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http |
| 24 | `zloi-user-socks5` | socks5 | **56** | https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt |
| 25 | `monosans_http` | http | **55** | https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt |
| 26 | `monosans/socks5` | socks5 | **47** | https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5 |
| 27 | `r00tee-socks5` | socks5 | **45** | https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt |
| 28 | `sunny9577-socks` | mixed | **44** | https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt |
| 29 | `Anonym0usWork-socks5` | socks5 | **44** | https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies |
| 30 | `proxyscrape-v4-http` | http | **41** | https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&format= |
| 31 | `hookzof-socks5` | socks5 | **40** | https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt |
| 32 | `proxifly-socks5` | socks5 | **40** | https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.tx |
| 33 | `proxifly-json-socks5` | socks5 | **40** | https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.json |
| 34 | `proxyscrape-v2-socks5` | socks5 | **39** | https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all |
| 35 | `proxifly-jsdelivr-socks5` | socks5 | **38** | https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt |
| 36 | `anonym0us_http` | http | **38** | https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.t |
| 37 | `proxyscrape-v2-legacy-http` | http | **37** | https://api.proxyscrape.com/?request=getproxies&proxytype=http |
| 38 | `proxyscrape-v3-http-json` | http | **37** | https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&format=j |
| 39 | `iplocate-socks5` | socks5 | **36** | https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks5.txt |
| 40 | `proxyscrape-v4-http-json` | http | **35** | https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&format= |

## 其余有贡献的源（41 名之后）

`proxyscrape-socks5`(33)、`ALIILAPRO-socks5`(32)、`free-proxy-list.net`(31)、`proxyscrape-v2-http`(30)、`MuRongPIG-socks5`(30)、`monosans_socks5`(29)、`free-proxy-list.net-anon`(28)、`sslproxies.org`(25)、`spys-me-socks-txt`(23)、`proxyspace-https`(18)、`proxyscrape-v2-elite-http`(17)、`proxyscrape-v4-socks4`(15)、`socks-proxy.net`(13)、`monosans/socks4`(11)、`spys-me-proxy-txt`(11)、`proxyscrape-socks4`(11)、`proxyscrape-v2-socks4`(10)、`monosans_socks4`(10)、`zloi-user-http`(8)、`iplocate-socks4`(8)、`proxifly-http`(7)、`my-proxy.com`(6)、`us-proxy.org`(6)、`shiftytr-http`(5)、`shiftytr`(5)、`proxifly_http`(5)、`my-proxy.com-p2`(5)、`proxifly-socks4`(4)、`ClearProxy-socks5`(4)、`zloi-user-socks4`(3)、`proxy_list_org_cn`(3)、`my-proxy.com-anonymous`(3)、`roosterkid-https`(2)、`my-proxy.com-transparent`(2)、`my-proxy.com-socks5`(2)、`vakhov-socks5`(1)、`jetkai-socks5`(1)、`roosterkid-socks5`(1)、`proxyscrape-v2-anonymous-http`(1)、`jetkai-socks4`(1)、`jetkai`(1)、`vakhov_socks5`(1)、`jhao104/ihuan`(1)、`my-proxy.com-elite`(1)

## 按分片

- `api-json`：28 个源有贡献
- `socks-focus`：22 个源有贡献
- `html-sites`：11 个源有贡献
- `pool-service`：10 个源有贡献
- `cn-region`：9 个源有贡献
- `longtail`：4 个源有贡献

## 用法

这批源活代理密度高，建议作为池子的**白名单/高优先抓取队列**。机读版：`data/sources_curated.json`（含每个源的可用代理明细）。

**注意时效**：免费代理源本身长期可用（GitHub raw / API 站点稳定），但**从源里捞到的具体 IP 寿命很短**——本次自报 ok 的 2,305 条，隔十几分钟实测只剩 10.5%。所以源要定期重抓，IP 要现测现用。
