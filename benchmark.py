def benchmark(client):
    client.set("key", 1)
    print(client.get("key"))