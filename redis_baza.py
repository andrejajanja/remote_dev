import redis, json; from hashlib import md5;

r = redis.Redis(host = "192.168.0.10", port = "49499", db=0)

lokacija = ["192.168.1.11", "123"]
param = ["aaa", "komp", "komanda", "l"]

user = r.get(param[0])
if user == None:            
    kalup= {
        param[1]: { "ip": lokacija[0]   }                
    }
    kalup[param[1]][param[3]] = lokacija[1]
    r.set(param[0], json.dumps(kalup))    
else:
    user = json.loads(user)
    user[param[1]][param[3]] = lokacija[1]
    r.set(param[0], json.dumps(user))

