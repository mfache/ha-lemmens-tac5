import asyncio
from pymodbus.client import AsyncModbusTcpClient

async def main():
    client = AsyncModbusTcpClient("192.168.1.55", port=502)
    await client.connect()
    
    res = await client.read_holding_registers(253, count=1)
    if not res.isError(): print(f"Init Flow (253): {res.registers[0]}")
    
    client.close()

asyncio.run(main())
