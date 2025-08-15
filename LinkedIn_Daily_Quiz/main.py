import requests
import my_info as me


ACCESS_TOKEN = me.ACCESS_TOKEN
PERSON_URN = me.PERSON_URN
LINKEDIN_UGC_URL = "https://api.linkedin.com/v2/ugcPosts"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
}

message = "Test posting using a python script."

payload = {
    "author": PERSON_URN,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": message},
            "shareMediaCategory": "NONE",
        }
    },
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
}

resp = requests.post(LINKEDIN_UGC_URL, headers=headers, json=payload)

print(resp.status_code)
print(resp.text)

data = resp.json()
urn = data["id"]
view_url = f"https://www.linkedin.com/feed/update/{urn}"
print(view_url)
