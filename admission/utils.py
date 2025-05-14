import requests

from core.models import Setting

def send_sms(phone_number, combined_message):
    setting = Setting.objects.first()

    if setting:
        instance_id = setting.instance_id
        access_token = setting.access_token
    else:
        instance_id = None
        access_token = None

    url = "https://cloudbusinesssender.com/api/send"

    payload = {
        "number": phone_number,
        "type": "text",
        "message": combined_message,
        "instance_id": instance_id,
        "access_token": access_token
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print("Response Status Code:", response.status_code)
        print("Response Body:", response.text)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Failed to send message: {e}")
        return False