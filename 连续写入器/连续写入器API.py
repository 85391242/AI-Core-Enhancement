# -*- coding: utf-8 -*-
"""连续写入器API.py · 体系写入通道API
POST /写 {路径,内容} → 连续写入（分块追加+原子替换+自愈）→ 返回结果
GET  /状态 → 服务健康
"""
import io, json, os
from http.server import HTTPServer, BaseHTTPRequestHandler

家 = os.path.dirname(os.path.abspath(__file__))


def 连续写入(路径, 内容, 块大小=800):
    块 = [内容[i:i + 块大小] for i in range(0, len(内容), 块大小)]
    临时 = 路径 + ".tmp"
    日志 = []
    for i, 段 in enumerate(块):
        成功 = "假"
        for 试 in range(3):
            try:
                with io.open(临时, "a", encoding="utf-8") as f:
                    f.write(段)
                成功 = "真"
                break
            except Exception:
                pass
        if 成功 == "假":
            return "失败：块%d" % i
        日志.append("块%d·相位%d" % (i + 1, i + 1))
    try:
        os.replace(临时, 路径)
    except Exception:
        return "失败：原子替换"
    return 日志


class 处理器(BaseHTTPRequestHandler):
    def _回(self, 体):
        b = json.dumps(体, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/status":
            self._回({"状态": "连续写入器API在线", "能力": "分块追加+原子替换+自愈", "轮次": 57})
        else:
            self._回({"错误": "未知路径·可用 /status 或 POST /write"})

    def do_POST(self):
        if self.path == "/write":
            try:
                长 = int(self.headers.get("Content-Length", 0))
                数据 = json.loads(self.rfile.read(长).decode("utf-8"))
                路径 = 数据.get("路径", "")
                内容 = 数据.get("内容", "")
                if not 路径 or not 内容:
                    self._回({"错误": "需路径与内容"})
                    return
                结果 = 连续写入(路径, 内容)
                self._回({"结果": 结果})
            except Exception as ex:
                self._回({"错误": str(ex)})
        else:
            self._回({"错误": "未知路径"})

    def log_message(self, *a):
        pass


HTTPServer(("127.0.0.1", 8898), 处理器).serve_forever()
