import requests
import json
from app.database import settings

r = requests.get(
    "https://www.ngxpulse.ng/api/ngxdata/prices/DANGCEM",
    headers={"X-API-Key": settings.NGX_PULSE_API_KEY},
    params={"days": 3},
    timeout=10
)
print(json.dumps(r.json(), indent=2))