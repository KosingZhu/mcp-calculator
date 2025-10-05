# 小智AI接入MCP能力指导文档

## 项目概述

本项目（xiaozhimcp）是一个强大的接口实现，用于通过远程控制、计算、文件操作、知识搜索等方式扩展AI能力。MCP（Model Context Protocol）是一种允许服务器向语言模型暴露可调用工具的协议，使AI能够与外部系统进行交互。

## 环境准备

### 1. 安装必要依赖

```bash
# 进入项目目录
e: && cd E:\AILearning\atomS3R\xiaozhimcp

# 安装项目依赖
pip install -r requirements.txt
```

### 2. 确认项目文件结构

当前项目包含以下关键文件：
- `mcp_pipe.py`: 主通信管道，处理WebSocket连接和进程管理
- `pc_operator.py`: PC操作工具实现（文件操作、截图等）
- `mcp_config.json`: MCP服务器配置文件
- `mcp_server_plugin.json`: 插件配置文件，用于本地mcp服务器使用http/sse协议启动服务
- `requirements.txt`: 项目依赖列表

## 接入方式一：自行编码实现MCP服务（stdio协议）

### 1. 原理说明

通过自行编写Python代码实现MCP服务，使用`FastMCP`类创建服务并注册自定义工具，通过标准输入输出（stdio）与小智AI设备通信。

### 2. 实现步骤

#### 2.1 创建自定义MCP工具

创建一个新的Python文件，例如`custom_mcp_tools.py`，并添加以下内容：

```python
from mcp.server.fastmcp import FastMCP
import logging
import sys

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('custom_mcp')

# 修复Windows控制台的UTF-8编码
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# 创建MCP服务器实例
mcp = FastMCP("custom_tools")

# 注册自定义工具
@mcp.tool()
def say_hello(name: str) -> str:
    """向指定名称的用户问好"""
    result = f"你好，{name}！欢迎使用自定义MCP工具。"
    logger.info(f"say_hello 结果: {result}")
    return result

@mcp.tool()
def calculate_sum(a: int, b: int) -> dict:
    """计算两个整数的和"""
    result = a + b
    logger.info(f"calculate_sum 结果: {a} + {b} = {result}")
    return {"result": result, "message": "计算成功"}

# 启动MCP服务器，使用stdio传输
if __name__ == "__main__":
    logger.info("自定义MCP服务已启动，等待连接...")
    mcp.run(transport="stdio")
```

#### 2.2 在配置文件中添加自定义服务

编辑`mcp_config.json`文件，添加自定义服务配置：

```json
"custom-tools": {
  "type": "stdio",
  "command": "python",
  "args": ["-m", "custom_mcp_tools.py"]
}
```

#### 2.3 运行自定义MCP服务

通过主程序启动所有配置的服务：

```bash
python mcp_pipe.py
```

或者直接运行单个自定义服务：

```bash
python mcp_pipe.py custom_mcp_tools.py
```

#### 2.4 验证服务

查看控制台输出，确认服务已成功启动，并且能够处理来自AI的请求。

## 接入方式二：使用npx/uvx接入外部开源MCP服务（stdio协议）

### 1. 原理说明

通过Node.js的npx命令或Bun的uvx命令直接运行外部开源的MCP服务，本质是将mcp服务部署至本地，通过stdio协议暴露给小智AI调用MCP提供的能力。

### 2. 实现步骤

#### 2.1 安装Node.js环境

确保已安装Node.js（推荐16.x及以上版本）。可以从[Node.js官网](https://nodejs.org/)下载安装包。

验证安装：

```bash
# 检查Node.js版本
node --version

# 检查npm版本
npm --version
```

#### 2.2 配置外部MCP服务

项目中已在`mcp_config.json`中配置了几种外部MCP服务：

- Playwright MCP服务
- git操作工具

示例配置：

```json
"Playwright_npx": {
  "type": "stdio",
  "command": "npx.cmd", # 注意windows下npx命令需要写成npx.cmd,否则python代码会找不到npx命令报错
  "args": ["-y", "@playwright/mcp@latest"]
},
"mcp-server-git": {
	"type": "stdio",
	"command": "uvx",
	"args": ["mcp-server-git"]
}
```

#### 2.3 运行外部MCP服务

通过主程序启动所有配置的服务：

```bash
python mcp_pipe.py
```

#### 2.5 配置WebSocket连接

确保已设置`MCP_ENDPOINT`环境变量，指向WebSocket服务器地址：

```bash
# Windows PowerShell
$env:MCP_ENDPOINT = "wss://api.xiaozhi.me/mcp/?token=xxx"
```

## 接入方式三：通过互联网远程调用MCP服务（SSE或HTTP协议）

### 1. 原理说明

通过互联网连接到远程MCP服务，使用SSE（Server-Sent Events）或HTTP协议进行通信，无需在本地运行MCP服务。

### 2. 实现步骤

#### 2.1 启用远程服务配置

编辑`mcp_config.json`文件，启用远程服务配置：

```json
"remote-sse-server": {
  "type": "sse",
  "url": "https://api.example.com/sse",
  "disabled": false  // false为启用
},
"remote-http-server": {
  "type": "http",
  "url": "https://api.example.com/mcp",
  "disabled": false
}
```

#### 2.2 配置代理服务

远程服务需要通过`mcp_proxy`进行代理，项目会自动处理这一步骤。确保已安装`mcp-proxy`依赖：

```bash
pip install mcp-proxy>=0.8.2
```

#### 2.3 运行远程服务连接

通过主程序启动所有配置的服务（包括已启用的远程服务）：

```bash
python mcp_pipe.py
```

#### 2.4 验证远程连接

查看控制台输出，确认已成功连接到远程MCP服务。程序会自动处理重连机制，如果连接断开，会尝试以指数退避的方式重新连接。

## 配置详解

### 1. mcp_config.json配置说明

`mcp_config.json`文件用于定义所有可用的MCP服务器配置：

- `type`: 传输类型，支持`stdio`、`sse`和`http`
- `command`: 对于`stdio`类型，指定要运行的命令
- `args`: 命令参数数组
- `url`: 对于`sse`和`http`类型，指定远程服务URL
- `disabled`: 是否禁用该服务

### 2. 环境变量配置

- `MCP_ENDPOINT`: WebSocket服务器端点地址
- `MCP_CONFIG`: 可选，指定替代的配置文件路径

### 3. MCP工具定义格式

每个MCP工具通过装饰器`@mcp.tool()`定义，并包含：
- 函数名称（工具标识符）
- 参数列表（带类型注解）
- 文档字符串（工具描述）
- 返回值（通常为字典或字符串）

## 高级功能

### 1. 自动重连机制

`mcp_pipe.py`实现了具有指数退避的自动重连机制，配置如下：
- 初始等待时间：1秒
- 最大等待时间：600秒

### 2. 服务管理

- 可以同时运行多个MCP服务（本地和远程）
- 支持启用/禁用特定服务
- 自动处理服务进程的启动、监控和终止

### 3. 自定义工具开发

开发自定义MCP工具时，可以利用以下功能：
- 支持多种参数类型（整数、字符串、布尔值等）
- 可以返回复杂的数据结构
- 内置日志系统，方便调试和监控

## 使用示例

### 1. 启动所有配置的MCP服务

```bash
python mcp_pipe.py
```

### 2. 运行单个特定的MCP服务

```bash
python mcp_pipe.py pc_operator.py
```

### 3. 创建新的MCP工具服务

参考`pc_operator.py`文件的实现方式：

```python
from mcp.server.fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("service_name")

# 注册工具
@mcp.tool()
def tool_name(parameter: type) -> return_type:
    """工具描述"""
    # 实现工具逻辑
    return result

# 启动服务
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## 项目依赖

项目使用以下主要依赖：
- websockets>=11.0.3
- mcp>=1.8.1
- pydantic>=2.11.4
- mcp-proxy>=0.8.2
- pillow>=10.4.0

## 总结

通过本指导文档，您已经了解了三种将小智AI接入MCP能力的方式：
1. **自行编码实现**：完全可控，可深度定制功能
2. **使用npx/uvx**：快速部署，无需手动安装依赖，利用开源优势，快速扩展AI能力
3. **远程调用**：无需本地运行服务，零维护成本

根据您的实际需求和环境条件，选择最适合的接入方式，即可为小智AI扩展丰富的功能。