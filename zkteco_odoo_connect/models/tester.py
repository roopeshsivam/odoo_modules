from zk import ZK, const    # type: ignore
import json
conn = None

host = 'IP or DNS'


# padelpoint-rasalkhor.freeddns.org

zk = ZK(host, port=4370, timeout=5, password=0, force_udp=False, ommit_ping=True)

try:
    conn = zk.connect()
    conn.disable_device()
    # conn.set_user(uid=12678, name='Odoo Bot', password='1234', group_id='', user_id='999', card=0)
    # users = conn.get_users()
    # user = any(map((lambda user: user.uid == 9199), users))
    # filter(lambda user: user.uid == 999, users)
    # print(users)
    # for record in users:
    #     if record.uid == 199:
    #         raise Exception('Stop')

    attendances = conn.get_attendance()
    for record in attendances:
    #    print(f"Name : {record.user_id}| Status: {record.status} | Punch : {record.punch}")
        print(record)

    conn.test_voice(index=11)
    conn.enable_device()
except Exception as e:
    print ("Process terminate : {}".format(e))
finally:
    if conn:
        conn.disconnect()