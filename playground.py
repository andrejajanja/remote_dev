import json

kalup= {
    "d": { "ip": "65464654654"   }                
}

f = json.dumps(kalup)
print(f"alkdjaklsdjas\n{f}\n")

x = json.loads(f)

print(x["d"])