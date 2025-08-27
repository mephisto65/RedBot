import requests
from langchain_core.tools import tool

#TODO privilege escalation module / answer handler

API_URL = "http://127.0.0.1:4444"  # TODO CONFIGURE API URL

@tool
def pentest_api_tool(action: str, command: str = None, pid: str = None) -> str:
    """
    Interact with the Pentest API. You have access to dictionaries at
    -  /usr/share/wordlists/rockyou.txt -- for password cracking
    -  /usr/share/wordlists/enumeration/directory_list_medium.txt -- for directory enumeration
    -  /usr/share/wordlists/enumeration/subdomains-110000.txt -- for subdomain enumeration
    - /usr/share/wordlists/dirb -- for directory brute-forcing

    You also have access to linpeas at /home/pentest/linpeas/linpeas.sh for privilege escalation enumeration on the target machine.

    Args:
        action: What to do. Options:
            - "health": check API health
            - "allowed": list allowed commands
            - "execute": run a command (needs 'command')
            - "execute_background" : run a command in background (needs 'command')
            - "get_process": get info about a background process (needs 'pid')
        command: The command to execute (only for action="execute")
        pid: The pid of the process to get info from (only for action="get_process")
    """
    try:
        if action == "health":
            r = requests.get(f"{API_URL}/health")
            return r.json()

        elif action == "allowed":
            r = requests.get(f"{API_URL}/commands/allowed")
            return r.json()

        elif action == "execute":
            if not command:
                return "❌ You must provide a command for 'execute'."
            payload = {"command": command}
            r = requests.post(f"{API_URL}/execute", json=payload)
            return r.json()
        elif action == "execute_interactive":
            if not command:
                return "❌ You must provide a command for 'execute_background'."
            payload = {"command": command}
            r = requests.post(f"{API_URL}/execute/background", json=payload)
            return r.json()
        elif action == "get_process":
            if not pid:
                return "❌ You must provide a pid for 'get_process'."
            r = requests.get(f"{API_URL}/process/{pid}")

        else:
            return "❌ Invalid action. Use 'health', 'allowed', or 'execute'."

    except Exception as e:
        return f"⚠️ Error communicating with API: {str(e)}"
