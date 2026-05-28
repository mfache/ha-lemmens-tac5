import asyncio
from pymodbus.client import AsyncModbusTcpClient

async def main():
    client = AsyncModbusTcpClient("192.168.1.55", port=502)
    await client.connect()
    
    print("--- Pressures ---")
    res = await client.read_holding_registers(65, count=1)
    if not res.isError(): print(f"Supply Pressure (65): {res.registers[0]}")
    res = await client.read_holding_registers(73, count=1)
    if not res.isError(): print(f"Exhaust Pressure (73): {res.registers[0]}")
    
    print("--- Reference Pressures (Alarms) ---")
    res = await client.read_holding_registers(62, count=3)
    if not res.isError(): 
        print(f"Ref Supply Pressure (62): {res.registers[0]}")
        print(f"Ref Exhaust Flow (63): {res.registers[1]}")
        print(f"Ref Exhaust Pressure (64): {res.registers[2]}")
        
    print("--- Deltas ---")
    res = await client.read_holding_registers(431, count=2)
    if not res.isError():
        print(f"Delta Supply (431): {res.registers[0]}")
        print(f"Delta Exhaust (432): {res.registers[1]}")
        
    client.close()

asyncio.run(main())
