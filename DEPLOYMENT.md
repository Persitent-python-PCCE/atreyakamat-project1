# SeatMeUp — Netlify Dev Local Proxy Setup

This document outlines how to run the **SeatMeUp** development stack locally behind **Netlify Dev** as a local development proxy.

---

## 1. Development Options

### Option A: Development without Netlify Dev
You can run the application directly using the Flask development server:
```bash
# Set environment mode to development
export FLASK_ENV=development

# Start the Flask development server
flask run --port=8000
```
- **Local URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### Option B: Development with Netlify Dev
For simulating a Netlify production routing layout locally, use the Netlify CLI development proxy.

1. **Install Netlify CLI** (globally via npm):
   ```bash
   npm install -g netlify-cli
   ```
2. **Launch Netlify Dev**:
   ```bash
   netlify dev
   ```

Netlify Dev will:
- Read `netlify.toml` configurations.
- Spin up the Gunicorn/Flask instance on target port `8000` via the command:
  `gunicorn app:app --bind 127.0.0.1:8000` (on Unix/WSL/POSIX) or cross-platform equivalent.
- Start a local development proxy server on port `8888`.
- Expose the application at: [http://localhost:8888](http://localhost:8888)

---

## 2. Configuration & URLs

- **Gunicorn WSGI Server Address (Direct)**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Netlify Dev Proxy Address**: [http://localhost:8888](http://localhost:8888)

> **Important Notice**:
> Netlify Dev is purely a **local development proxy** used to simulate routing rules, redirects, or headers locally. It is not an internet-facing production tunnel.
