# Python Side
1. DOWNLOAD PYTHON
2. then run all these commands on your terminal
`pip install requests`
`pip install scratchattach`
3. download `sgptapi.py`
4. set the environment variables before running the script:

```bash
export SCRATCH_USERNAME="your_username"
export SCRATCH_PASSWORD="your_password"
# or, for online IDEs / blocked IPs, use a Scratch session id instead:
export SCRATCH_SESSION_ID="your_session_id"
export SCRATCH_PROJECT_ID="your_project_id"
```

5. run the script forever

If Scratch rejects your username/password from this environment, `SCRATCH_SESSION_ID` is the recommended fallback because many online IDEs and hosted runners are blocked by Scratch's login endpoint.

This project is not fully complete; it can consume more RAM as more people connect.
