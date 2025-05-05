import socket
import psycopg2
from psycopg2 import OperationalError
from datetime import timedelta, datetime
import pytz

myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = input("Enter Host IP Address (for example 127.0.0.1): ")
host_port = int(input("Enter Port Number (1-65535): "))
myTCPSocket.bind((host_ip, host_port)) ## binds to host's own private ip address and
myTCPSocket.listen(5)                  ## chosen port number
print("Server is listening.")

neon_str = "postgresql://neondb_owner:npg_phHQ9WujkR4F@ep-broad-credit-a4rjw3vc-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

class Q_solver:
    def __init__(self, d_conn):
        self.d_conn = d_conn
        self.moisture_data = []
        self.water_data = []
        self.electricity_data = {'kfridge': [], 'sfridge': [], 'dwasher': []}
        self._load_data()

    def _load_data(self):
        with self.d_conn.cursor() as c:
            # moisture data
            c.execute("""SELECT "assetUid" FROM smart_fridge_data_metadata WHERE "assetType" = 'Kitchen Fridge'""")
            kfridge = c.fetchone()
            c.execute("""SELECT payload->>'Moisture Meter - Moisture Sensor', "updatedAt" 
                         FROM smart_fridge_data_virtual 
                         WHERE payload->>'parent_asset_uid' = %s""", (kfridge[0],))
            for value, timestamp in c:
                if value is not None:
                    self.moisture_data.append((float(value), timestamp))

            # water data
            c.execute("""SELECT "assetUid" FROM smart_fridge_data_metadata WHERE "assetType" = 'Smart Dishwasher'""")
            dwasher = c.fetchone()
            c.execute("""SELECT payload->>'Float Switch - Water Usage Sensor', "updatedAt" 
                         FROM smart_fridge_data_virtual 
                         WHERE payload->>'parent_asset_uid' = %s""", (dwasher[0],))
            for value, timestamp in c:
                if value is not None:
                    self.water_data.append(float(value))

            # electricity data
            c.execute("""SELECT payload->>'ACS712 - Ammeter', 
                                payload->>'Duplicate Ammeter', 
                                payload->>'ACS712 - Dishwasher Ammeter', 
                                "updatedAt" 
                         FROM smart_fridge_data_virtual""")
            for kfridge_val, sfridge_val, dwasher_val, timestamp in c:
                if kfridge_val:
                    self.electricity_data['kfridge'].append(float(kfridge_val))
                if sfridge_val:
                    self.electricity_data['sfridge'].append(float(sfridge_val))
                if dwasher_val:
                    self.electricity_data['dwasher'].append(float(dwasher_val))

    def query(self, q):
        if q == 1:
            # Calculate average moisture of kitchen fridge from the past 3 hours
            end_time = datetime.now(pytz.UTC)
            start_time = end_time - timedelta(hours=3)
            
            relevant_data = [
                value for value, timestamp in self.moisture_data
                if start_time <= timestamp <= end_time
            ]

                
            avg_moisture = sum(relevant_data) / len(relevant_data)
            return f"Avg smart fridge moisture from the last three hours: {avg_moisture:.2f}% RH"

        elif q == 2:
            # Calculate average water usage of smart dishwasher per cycle
                
            avg_water = sum(self.water_data) / len(self.water_data)
            return f"Avg smart dishwasher water consumption per cycle: {avg_water:.2f} L"

        elif q == 3:
            # Calculate device with highest electricity usage (between all three devices)

            totals = {
                device: sum(values) 
                for device, values in self.electricity_data.items()
            }
            highest = max(totals.items(), key=lambda x: x[1])
            return f"Highest consumption was {highest[0]}: {highest[1]:.2f}kWh"
            
        else:
            return "Invalid query number"

while True:
    incomingSocket, incomingAddress = myTCPSocket.accept() ## accepts connection
    print("Connected to partner.")
    while True:
        myData = incomingSocket.recv(1024) ## takes msg from client
        if myData:
            conn = psycopg2.connect(neon_str)
            solver = Q_solver(conn)
            c_msg = int(myData.decode())
            response = solver.query(c_msg)
            print(f"Server response: {response}")
            incomingSocket.send(bytearray(str(response), encoding='utf-8')) ## sends capitalized msg back
        else:
            conn.close()
            print("Connection closed.")
            break
    incomingSocket.close()
    break
