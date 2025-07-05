import requests

LOG_SERVER_URL = "https://log-service.campus.stirringminds.in/logs"
CLIENT_ID = "7dc4c7ac-4a66-4b55-8f47-f0b676e2721f"
CLIENT_SECRET = "FXtjGHbhxPSKPXkt"

VALID_STACKS = {"backend", "frontend"}
VALID_LEVELS = {"debug", "info", "warn", "error", "fatal"}
VALID_PACKAGES = {
    "backend": {"cache", "controller", "cron_job", "domain", "handler", "repository", "route", "service"},
    "frontend": {"api", "component", "hook", "page", "state", "style"},
    "both": {"auth", "config", "middleware", "utils"}
}

def Log(stack: str, level: str, package: str, message: str):
    stack, level, package = stack.lower(), level.lower(), package.lower()
    if stack not in VALID_STACKS:
        raise ValueError(f"Invalid stack: {stack}")
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid level: {level}")
    if package not in VALID_PACKAGES.get(stack, set()) and package not in VALID_PACKAGES["both"]:
        raise ValueError(f"Invalid package: {package} for stack: {stack}")

    payload = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }
    headers = {
        "Content-Type": "application/json",
        "clientID": "7dc4c7ac-4a66-4b55-8f47-f0b676e2721f",
        "clientSecret": "FXtjGHbhxPSKPXkt"
    }

    try:
        response = requests.post(LOG_SERVER_URL, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            print("[Log Success]", response.json().get("logID"))
        else:
            print(f"[Log Error] {response.status_code} {response.text}")
    except Exception as e:
        print("[Log Exception]", str(e))