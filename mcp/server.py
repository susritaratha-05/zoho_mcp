from mcp.server.fastmcp import FastMCP
from tools.leave_tools import registerable_tools as leave_tools

mcp    = FastMCP("prodevans-hr-mcp", port=8001)

all_tools = (
    leave_tools()
)

for tool in all_tools():
    mcp.tool()(tool)

if __name__ == "__main__":
    mcp.run(transport="sse")