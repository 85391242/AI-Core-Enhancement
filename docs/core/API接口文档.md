# API接口文档

## 1. 基础规范
### 1.1 请求格式
```http
POST /api/v1/service HTTP/1.1
Host: api.example.com
X-Auth-Token: {国密加密token}
Content-Type: application/json
Body: {"param1":"值1","param2":"值2"}
```

### 1.2 响应格式
```json
{
  "code": 200,
  "data": {
    "field1": "值1",
    "field2": 123
  },
  "sign": "SM3签名值"
}
```

## 2. 核心接口
### 2.1 数据查询接口
`GET /api/v1/data/{id}`

| 参数 | 类型 | 必填 | 说明               |
|------|------|-----|--------------------|
| id   | int  | 是  | 数据唯一标识        |
| type | string | 否 | 数据分类(默认all)  |

### 2.2 批量操作接口
`POST /api/v1/batch`

```python
# 请求示例
import requests
url = "https://api.example.com/api/v1/batch"
headers = {"X-Auth-Token": "your_token"}
data = {"operations": [...]}
response = requests.post(url, json=data, headers=headers)
```

## 3. 安全机制
### 3.1 签名算法
1. 参数按key排序
2. 拼接成query字符串
3. SM3哈希运算
4. Base64编码

### 3.2 流量控制
| 等级 | QPS限制 | 超额处理       |
|------|--------|---------------|
| 普通 | 100    | 排队等待       |
| VIP  | 500    | 弹性扩容       |