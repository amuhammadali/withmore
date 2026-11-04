import urllib.request

redirect_url = "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQLDHldSu9CKml2tMYKk9fmfOAzqGzCUwxCuUpvNrzud9K6m92uLuFd1dmlNVGsGYyIfn5RaYLW0aB6cy9SM5LHbYa61yWQe6msXd57rQbaj-bScnFkQSr7sRLyqs0aDQj"
req = urllib.request.Request(redirect_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Final URL:", resp.geturl())
except Exception as e:
    print("Err:", e)

