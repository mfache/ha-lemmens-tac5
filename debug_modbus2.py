import asyncio
from pymodbus.client import AsyncModbusTcpClient

async def main():
    client = AsyncModbusTcpClient("192.168.1.55", port=502)
    await client.connect()
    
    res = await client.read_holding_registers(254, count=1)
    if not res.isError(): print(f"Init Flow (254): {res.registers[0]}")
    
    res = await client.read_holding_registers(61, count=4)
    if not res.isError(): 
        print(f"Ref Supply Flow (61): {res.registers[0]}")
        print(f"Ref Supply Pressure (62): {res.registers[1]}")
        print(f"Ref Exhaust Flow (63): {res.registers[2]}")
        print(f"Ref Exhaust Pressure (64): {res.registers[3]}")

    res = await client.read_holding_registers(64, count=11)
    if not res.isError(): 
        print(f"Current Supply Flow (64): {res.registers[0]}")
        print(f"Current Supply Pressure (65): {res.registers[1]}")
        print(f"Current Exhaust Flow (72): {res.registers[8]}")
        print(f"Current Exhaust Pressure (73): {res.registers[9]}")
        
    client.close()

asyncio.run(main())
