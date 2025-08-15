import requests

LINKEDIN_UGC_URL = "https://api.linkedin.com/v2/ugcPosts"

def post_text_update(access_token: str, person_urn: str, message: str, visibility: str = "CONNECTIONS"):
    """
    visibility: 'PUBLIC' or 'CONNECTIONS'
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": message},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
    }

    return requests.post(LINKEDIN_UGC_URL, headers=headers, json=payload)