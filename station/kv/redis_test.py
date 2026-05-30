from redis_kv import Redis
import json


# Create an instance of Redis
redis_instance = Redis()

# Set each value individually
redis_instance.create('state', 'idle')
redis_instance.create('response', 'qr-code')
redis_instance.create('am', 0.0)
redis_instance.create('current_kwh', 0.0)
redis_instance.create('chargingStation', 1)
redis_instance.create('sliderCounts', 1)
redis_instance.create('timerSlideChange', 2000)
redis_instance.create('total_kwh', 0.0)
redis_instance.create('created_at', 1684324007000)
redis_instance.create('start_payed', "null")
redis_instance.create('freeTime', 17828)


# Define the JSON object
json_data = {
    "lot": {
        "uid": "KRD_KONGRESSNAYA_31",
        "spaces": [
            {
                "charge_type": "TES_US",
                "name": "002",
                "id": 2,
                "uid": "KRD_KONGRESSNAYA_31_2_TESLA_EU",
                "price_kw": 10.0,
                "price_hour": 100.0,
                "parklock_mac": "E2:4C:2E:15:10:71",
                "meter_com_port": "/dev/ttyUSB0",
                "meter_code": 65,
                "red_pin_number": 11,
                "green_pin_number": 13,
                "blue_pin_number": 15,
                "parklock_led_pin_number": 37,
                "sonic_led_pin_number": 35,
                "sonic_trigger_pin_number": 31,
                "sonic_echo_pin_number": 33,
                "reed_switch_pin_number": 29,
                "active_amp": 12,
                "sonic_floor_distance": 264.0,
                "sonic_car_distance": 250.0,
                "meter_model": "M_234_ARTM2_02_POBR_R",
                "connectors": [
                    {
                        "connector_type": "TES_US",
                        "phases_count": 1,
                        "max_kw": 20.0,
                        "max_a": 80.0,
                        "relay_pin_number": None
                    }
                ]
            }
        ],
        "cameras": [
            {
                "id": 2,
                "name": "CAM 1",
                "ip": "10.0.0.14",
                "rtsp_url": "rtsp://10.0.0.14:554/user=admin&password=&channel=1&stream=0.sdp/"
            },
            {
                "id": 3,
                "name": "CAM 2",
                "ip": "10.0.0.10",
                "rtsp_url": "rtsp://10.0.0.10:554/user=admin&password=&channel=1&stream=0.sdp/"
            }
        ]
    }
}

# Convert the JSON object to a string
json_string = json.dumps(json_data)

# Set the value in Redis
redis_instance.update('settings', json_string)


print(redis_instance.get_all())

print(redis_instance.get_all().get('response'))