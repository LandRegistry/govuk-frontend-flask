![Static Badge](https://img.shields.io/badge/GOV.UK%20Frontend-v5.14.0-blue)

# GOV.UK Frontend - Flask App Template

Start building **accessible**, **secure**, **production-ready** and **maintainable** GOV.UK-style services, fast.

A [Flask](https://flask.palletsprojects.com) application integrating the [GOV.UK Design System](https://design-system.service.gov.uk/) with a realistic, containerised stack.

> **GOV.UK Frontend Flask App Template is a [community tool](https://design-system.service.gov.uk/community/resources-and-tools/) of the [GOV.UK Design System](https://design-system.service.gov.uk/). The Design System team is not responsible for it and cannot support you with using it. Contact the [maintainers](#contributors) directly if you need [help](#support) or you want to request a feature.**

## Highlights

- **GOV.UK components built in** – Accessible [Jinja templates](https://github.com/LandRegistry/govuk-frontend-jinja) and [WTForms helpers](https://github.com/LandRegistry/govuk-frontend-wtf) for compliant UI and forms.
- **Secure Flask foundation** – HTTPS, CSRF, CSP, rate limits, [SQLAlchemy](https://www.sqlalchemy.org/) and migrations ready to go.
- **Containerised by default** – [Nginx](https://nginx.org/en/) , [PostgreSQL](https://www.postgresql.org/), [Valkey](https://valkey.io/) and [Node](https://nodejs.org/en) pipeline managed via [Docker Compose](https://docs.docker.com/compose/).
- **Fast, lean builds** – Multi-stage Dockerfiles, wheel caching, non-root runtime, and CI via [GitHub Actions](https://github.com/features/actions).
- **Compliance-ready pages** – 404/500 errors, cookie banner, accessibility statement and privacy notice included.
- **Developer-first setup** – Example blueprints, templates, macros, and GOV.UK-style flash messages for instant feedback.

## Security

Secure by default with hardened containers, strong HTTP headers and built-in rate limiting.

- Applies strict CSP, HSTS, and other security headers.
- CSRF protection via Flask-WTF, with safe error handling.
- Rate limiting backed by Valkey using Flask-Limiter.
- Non-root containers with read-only filesystem for runtime services.
- Secrets and credentials injected via environment variables (no in-repo secrets).
- Dependency scanning and Python version pinning via CI workflows.

## Performance

Optimised for speed and reliability through caching, minimal layers and lean builds.

- Multi-stage Docker builds minimise image size and attack surface.
- Static assets compiled once and cached efficiently.
- Connection pooling for SQLAlchemy database access.
- Valkey caching support for transient or computed data.
- Nginx configured for compression and cache control.
- CI validates image build times and wheel caching efficiency.

## Developer Experience

Built to feel frictionless for rapid iteration, testing and deployment.

- Works identically across local and production environments.
- Uses docker compose watch for hot reloads of Python and static assets.
- Includes blueprints, forms, templates and example routes to extend quickly.
- Built-in error pages, logging and debug toolbar (development mode).
- Extensive comments and .env.example for easy onboarding.
- CI workflows for linting, tests, builds and security scans.

## Requirements

- Docker (Engine & Compose)

## Quick start

### 1. Create a new repository

[Create a new repository](https://github.com/LandRegistry/govuk-frontend-flask/generate) using this template, with the same directory structure and files. Then clone a local copy of your newly created repository.

### 2. Configure environment

Create a `.env` file in the root of the repo and enter your specific config based on this example:

```dotenv
CONTACT_EMAIL=[contact email]
CONTACT_PHONE=[contact phone]
DEPARTMENT_NAME=[name of department]
DEPARTMENT_URL=[url of department]
ONE_LOGIN_ACCESS_TOKEN_URL=http://govuk-one-login:3000/token
ONE_LOGIN_AUTHORIZE_URL=http://localhost:3000/authorize
ONE_LOGIN_CLIENT_ID=HGIOgho9HIRhgoepdIOPFdIUWgewi0jw
ONE_LOGIN_JWKS_URL=http://govuk-one-login:3000/.well-known/jwks.json
ONE_LOGIN_PRIVATE_KEY_PATH=app/govuk_one_login_private_key.pem
ONE_LOGIN_PUBLIC_TOKEN_URL=http://localhost:3000/token
ONE_LOGIN_USERINFO_URL=http://govuk-one-login:3000/userinfo
POSTGRES_DB=db
POSTGRES_HOST=db
POSTGRES_PASSWORD=db_password
POSTGRES_PORT=5432
POSTGRES_USER=db_user
SECRET_KEY=[see below]
SERVICE_NAME=[name of service]
SERVICE_PHASE=[phase]
SERVICE_URL=[url of service]
VALKEY_HOST=cache
VALKEY_PORT=6379
```

You **must** set a new `SECRET_KEY`, which is used to securely sign the session cookie and CSRF tokens. It should be a long random `bytes` or `str`. You can use the output of this Python command to generate a new key:

```shell
python -c 'import secrets; print(secrets.token_hex())'
```

### 3. Start the stack

```shell
docker compose up --build
```

Visit <https://localhost/> and accept the browser’s security warning.

Hot reloading is supported via:

```shell
docker compose watch
```

> **Note**: `docker compose watch` requires Docker Compose v2.22 or newer.

## Testing

Run unit tests and measure coverage locally:

```shell
python -m pytest --cov=app --cov-report=term-missing --cov-branch
```

## Environment

| Service          | Role                              | Container         | Port exposed     |
| ---------------- | --------------------------------- | ----------------- | ---------------- |
| Nginx            | Reverse proxy + HTTPS termination | `web`             | 443 (HTTPS) / 80 |
| Flask            | Web framework                     | `app`             | 5000             |
| PostgreSQL       | Relational database               | `db`              | 5432             |
| Valkey           | Server-side sessions and caching  | `cache`           | 6379             |
| GOV.UK One Login | OIDC Provider                     | `govuk-one-login` | 3000             |

## Architecture

### Container stack

This project uses Docker Compose to provision containers:

```mermaid
flowchart TB
    compose(compose.yml)
    nginx(nginx:stable-alpine)
    node(node:kyrpton-alpine)
    one-login(govuk-one-login/simulator:latest)
    postgres(postgres:18-alpine)
    python(python:3.14-slim)
    valkey(valkey/valkey:9-alpine)

    compose -- Creates --> App & Cache & Web & Database & onelogin
    App -- Depends on --> Cache & Database
    Web -- Depends on --> App

    subgraph Web
        direction TB
        node -- COPY /dist /static --> nginx
    end

    subgraph App
        python
    end

    subgraph Database
        postgres
    end

    subgraph Cache
        valkey
    end

    subgraph onelogin [One Login]
        one-login
    end
```

### Request flow

```mermaid
flowchart TB
    browser([Browser])
    db@{ shape: cyl, label: "PostgreSQL" }
    flask(Gunicorn/Flask)
    nginx(Nginx)
    static@{ shape: lin-cyl, label: "Static files" }
    valkey@{ shape: cyl, label: "Valkey" }
    one-login(GOV.UK One Login)

    browser -- https:443 --> nginx -- http:5000 --> flask -- postgres:5432 --> db
    browser -- http:3000 --> one-login
    flask -- redis:6379 --> valkey
    flask -- http:3000 --> one-login

    subgraph Docker Network
        subgraph Web
            nginx -- Read --> static
        end

        subgraph App
            flask
        end

        subgraph Database
            db
        end

        subgraph Cache
            valkey
        end
    end
```

## GOV.UK One Login

This template uses the GOV.UK One Login Simulator to provide realistic OIDC authentication.

### Configure

Once the `govuk-one-login` container is up and running:

```shell
curl --request POST \
  --url http://localhost:3000/config \
  --header 'content-type: application/json' \
  --data '{
    "clientConfiguration": {
      "redirectUrls": ["https://localhost/callback"],
      "postLogoutRedirectUrls": ["https://localhost/logged-out"]
    }
  }'
```

### Login

```mermaid
sequenceDiagram
    autonumber
    participant Browser
    participant Web as Nginx
    participant App as Flask
    participant Cache as Valkey
    participant Simulator

    Browser->>Web: GET https://localhost/login
    Web->>App: GET http://app:5000/login
    App->>Cache: SET session[state, nonce]
    App-->>Browser: Redirect to http://localhost:3000/authorize

    Browser->>Simulator: GET http://localhost:3000/authorize?client_id=...&redirect_uri=https://localhost/callback&state=...&nonce=...
    Simulator-->>Browser: Show login page
    Browser->>Simulator: User submits credentials
    Simulator-->>Browser: Redirect to https://localhost/callback?code=...&state=...

    Browser->>Web: GET https://localhost/callback?code=...&state=...
    Web->>App: GET http://app:5000/callback?code=...&state=...
    App->>Cache: GET session[state]
    App->>Simulator: POST http://govuk-one-login:3000/token
    Simulator-->>App: Return tokens (id_token, access_token)
    App->>Simulator: GET http://govuk-one-login:3000/.well-known/jwks.json
    Simulator-->>App: JWKS
    App->>Cache: SET session[user, tokens]
    App-->>Browser: Redirect to https://localhost/
```

### Logout

```mermaid
sequenceDiagram
    autonumber
    participant Browser
    participant Web as Nginx
    participant App as Flask
    participant Cache as Valkey
    participant Simulator

    Browser->>Web: GET https://localhost/logout
    Web->>App: GET http://app:5000/logout
    App->>Cache: GET session[user]
    App->>Cache: DELETE session
    App-->>Browser: Redirect to http://localhost:3000/logout
    Browser->>Simulator: GET http://localhost:3000/logout?id_token_hint=...&post_logout_redirect_uri=https://localhost/logged-out&state=...
    Simulator-->>Browser: Redirect to https://localhost/logged-out
    Browser->>Web: GET https://localhost/logged-out?state=...
    Web->>App: GET http://app:5000/logged-out?state=...
    App-->>Browser: Show logged out page
```

## Maintainers

- [Matt Shaw](https://github.com/matthew-shaw) - Principal Software Developer at HM Land Registry

## Support

This software is provided _"as-is"_ without warranty. Support is provided on a _"best endeavours"_ basis by the maintainers and open source community.

For questions or suggestions, reach out to the maintainers listed [above](#maintainers) and the community of people using this project in the [#govuk-design-system](https://ukgovernmentdigital.slack.com/archives/C6DMEH5R6) Slack channel.

Otherwise, please see the [contribution guidelines](CONTRIBUTING.md) for how to raise a bug report or feature request.
