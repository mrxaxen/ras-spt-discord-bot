import zlib
import httpx

client = httpx.Client()
# response = client.get('http://rockandstone.servebeer.com:6969/launcher/ping')
response = client.get('http://rockandstone.servebeer.com:6969/fika/presence/get')
decompressed = zlib.decompress(response.content)
print(decompressed)
