// arg: Name Units Place UpdateTime

start "Emulator: DHT-1" python emulator.py DHT-1 Celsius Room_1 7  
timeout 3 
start "Emulator: DHT-2" python emulator.py DHT-2 Celsius Common 11
timeout 3
start "Emulator: Electricity&Water Meter" python emulator.py ElecWaterMeter kWh Home 13
timeout 3
start "Emulator: Airconditioner" python emulator.py Airconditioner Celsius air-1 5
timeout 3
start "Emulator: Freezer" python emulator.py Freezer Celsius freezer 6
timeout 3
start "Emulator: Boiler" python emulator.py Boiler Celsius boiler 8
timeout 3
start "Emulator: Refrigerator" python emulator.py Refrigerator Celsius refrigerator 9
timeout 3
start "Smart Home Manager" python manager.py
timeout 10
start "System GUI" python gui.py