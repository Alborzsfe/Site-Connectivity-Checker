# Website Availability Checker

A small Streamlit application that checks multiple public websites concurrently and reports their HTTP status.

## Improvements and safeguards

- Accepts domains with or without an explicit `http://` or `https://` scheme.
- Sends one request per website instead of duplicate requests.
- Checks multiple websites concurrently.
- Rejects local, private, loopback, and link-local destinations to reduce SSRF risk.
- Limits each batch to 25 URLs and applies request timeouts.
- Includes automated tests and GitHub Actions.

## Run locally

```bash
git clone https://github.com/Alborzsfe/Site-Connectivity-Checker.git
cd Site-Connectivity-Checker
python -m venv .venv
```

Activate the environment, then install and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Enter one website per line, for example:

```text
example.com
https://openai.com
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Security note

This project resolves hostnames and blocks non-public IP addresses before requesting a URL. It is still a demonstration project, not a full production monitoring service. Production deployments should also enforce network-level egress restrictions.

## License

MIT
