# server.py
from mcp.server.fastmcp import FastMCP
import os
import sys
import logging
import tempfile
import tkinter
from PIL import ImageGrab

logger = logging.getLogger('operator')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Create an MCP server
mcp = FastMCP("operator")

# Add an addition tool
@mcp.tool()
def list_files(current_directory: str) -> str:
    """Get the list of files in the directory and return their names and types."""
    entries = [f"{i.name} ({'file' if i.is_file() else 'dir'})" for i in os.scandir(current_directory)]
    result = "\n".join(entries)
    logger.info(f"list_files_str result:\n{result}")
    return result

@mcp.tool()
def read_file(path: str) -> str:
    """读取文件内容"""
    with open(path, "r", encoding='utf-8') as f:
        return f.read()

@mcp.tool()
def open_file_with_default_app(file_path) -> str:
    """
    使用系统默认程序打开指定文件，效果等同于用户双击
    :param file_path: 文件的完整路径
    """
    try:
        os.startfile(file_path)
        msg = f"已用默认程序打开: {file_path}"
        logger.info(msg)
        return msg
    except Exception as e:
        msg = f"打开文件失败: {e}"
        logger.info(msg)        
        return msg

@mcp.tool()
def screenshot() -> str:
    """截屏并返回本地临时文件地址"""
    # 获取屏幕尺寸
    win = tkinter.Tk()
    width = win.winfo_screenwidth()
    height = win.winfo_screenheight()
    win.destroy()  # 关闭临时窗口

    # 截取全屏并转换为 RGB 模式
    img = ImageGrab.grab(bbox=(0, 0, width, height)).convert("RGB")

    # 生成临时文件路径 (更低级的方式)
    fd, temp_path = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    img.save(temp_path)
    logger.info(f"screenshot:\n{temp_path}")
    return temp_path

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
