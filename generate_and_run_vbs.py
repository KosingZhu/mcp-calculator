import json
import re
import subprocess
import time

CONFIG_PATH = r"E:\AILearning\atomS3R\xiaozhimcp\mcp_config.json"
PLUGIN_PATH = r"E:\AILearning\atomS3R\xiaozhimcp\mcp_server_plugin.json"
VBS_PATH = r"E:\AILearning\atomS3R\xiaozhimcp\run_mcp_all_silent.vbs"

def extract_port_from_url(url):
    if not url:
        return None
    m = re.search(r":(\d+)(?:/|$)", url)
    if m:
        return m.group(1)
    return None

def main():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    with open(PLUGIN_PATH, encoding="utf-8") as f:
        plugin = json.load(f)

    mcp_servers = config.get("mcpServers", {})
    plugin_servers = plugin.get("mcpServers", {})

    vbs_lines = [
        'Set WshShell = CreateObject("WScript.Shell")',
        ''
    ]
    run_cmd_count = 0

    for name, node in mcp_servers.items():
        node_type = node.get("type")
        disabled = node.get("disabled", False)
        if node_type in ("http", "sse", "streamablehttp") and not disabled and name in plugin_servers:
            cmd = plugin_servers[name].get("command")
            args = plugin_servers[name].get("args", [])
            url = node.get("url", "")
            port = extract_port_from_url(url)
            new_args = []
            port_set = False
            i = 0
            while i < len(args):
                if args[i] == "--port":
                    new_args.append("--port")
                    if port:
                        new_args.append(str(port))
                        port_set = True
                        i += 2
                        continue
                    elif i+1 < len(args):
                        new_args.append(str(args[i+1]))
                        port_set = True
                        i += 2
                        continue
                new_args.append(str(args[i]))
                i += 1
            if port and not port_set:
                new_args += ["--port", str(port)]
            cmdline = ' '.join([cmd] + new_args)
            vbs_lines.append(f'WshShell.Run "cmd /c {cmdline}", 0')
            run_cmd_count += 1

    vbs_lines.append('Set WshShell = Nothing')

    with open(VBS_PATH, "w", encoding="utf-8") as f:
        f.write('\n'.join(vbs_lines))
    print(f"VBS 脚本已生成: {VBS_PATH}")

    if run_cmd_count > 0:
        proc = subprocess.Popen(["wscript", VBS_PATH])
        print(f"VBS 脚本已启动，wscript 进程号: {proc.pid}")
        time.sleep(2)
        try:
            ps_cmd = [
                "cmd",
                "/c",
                "tasklist | findstr node"
            ]
            result = subprocess.check_output(ps_cmd, encoding='utf-8', errors='ignore')
            # 解析每一行，node.exe 后第一个数字为进程号
            node_pids = []
            for line in result.splitlines():
                m = re.search(r"node\.exe\s+(\d+)", line)
                if m:
                    node_pids.append(m.group(1))
            if node_pids:
                print(f"node 进程号: {', '.join(node_pids)}")
            else:
                print("未检测到 node 进程。")
        except Exception as e:
            print(f"获取 node 进程号失败: {e}")
    else:
        print("未生成任何有效的后台运行命令，VBS 脚本不会被执行。")

if __name__ == "__main__":
    main()