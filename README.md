# GOV.UK Frontend Flask

This is a template [Flask](https://flask.palletsprojects.com) app using the [GOV.UK Frontend](https://frontend.design-system.service.gov.uk/) and [GOV.UK Design System](https://design-system.service.gov.uk/) which is designed to get a new project started quicker. It is also a reference implementation of two core packages:

- [GOV.UK Frontend Jinja](https://github.com/LandRegistry/govuk-frontend-jinja) which provides Jinja macros of GOV.UK components
- [GOV.UK Frontend WTForms](https://github.com/LandRegistry/govuk-frontend-wtf) which provides WTForms widgets to integrate the above Jinja macros into form generation and validation

The app is provided intentionally bare, with just the essential parts that all services need, such as error pages, accessibility statement, cookie banner, cookie page and privacy notice. It uses a number of other packages to provide the [features](#features) described below with sensible and best-practice defaults. Please read the [next steps](#next-steps) section for guidance on how to start building out your app on top of this template.

## Prerequisites

### Required

- Python 3.7.x or higher

### Optional

- Redis 4.0.x or higher (for rate limiting, otherwise in-memory storage is used)

## Getting started

### Create a new repository

[Create a new repository](https://github.com/LandRegistry/govuk-frontend-flask/generate) using this template, with the same directory structure and files. Then clone a local copy of your newly created repository.

### Create venv and install requirements

```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt ; pip3 install -r requirements_dev.txt
```

### Get GOV.UK Frontend assets

For convenience a shell script has been provided to download and extract the GOV.UK Frontend distribution assets

```shell
./build.sh
```

### Set local environment variables

In the `.flaskenv` file you will find a number of environment variables. These are injected as global variables into the app and pre-populated into page templates as appropriate. Enter your specific information for the following:

- CONTACT_EMAIL
- CONTACT_PHONE
- DEPARTMENT_NAME
- DEPARTMENT_URL
- SERVICE_NAME
- SERVICE_PHASE
- SERVICE_URL

### Run app

```shell
flask run
```

You should now have the app running on <http://localhost:5000/>

## Testing

To run the tests:

```shell
python -m pytest --cov=app --cov-report=term-missing --cov-branch
```

## Features

Please refer to the specific packages documentation for more details.

### Asset management

Custom CSS and JavaScript files are merged and compressed using [Flask Assets](https://flask-assets.readthedocs.io/en/latest/) and [Webassets](https://webassets.readthedocs.io/en/latest/). This takes all `*.css` files in `app/static/src/css` and all `*.js` files in `app/static/src/js` and outputs a single compressed file to both `app/static/dist/css` and `app/static/dist/js` respectively.

CSS is [minified](https://en.wikipedia.org/wiki/Minification_(programming)) using [CSSMin](https://github.com/zacharyvoase/cssmin) and JavaScript is minified using [JSMin](https://github.com/tikitu/jsmin/). This removes all whitespace characters, comments and line breaks to reduce the size of the source code, making its transmission over a network more efficient.

### Cache busting

Merged and compressed assets are browser cache busted on update by modifying their URL with their MD5 hash using [Flask Assets](https://flask-assets.readthedocs.io/en/latest/) and [Webassets](https://webassets.readthedocs.io/en/latest/). The MD5 hash is appended to the file name, for example `custom-d41d8cd9.css` instead of a query string, to support certain older browsers and proxies that ignore the querystring in their caching behaviour.

### Forms generation and validation

Uses [Flask WTF](https://flask-wtf.readthedocs.io/en/stable/) and [WTForms](https://wtforms.readthedocs.io) to define and validate forms. Forms are rendered in your template using regular Jinja syntax.

### Form error handling

If a submitted form has any validation errors, an [error summary component](https://design-system.service.gov.uk/components/error-summary/) is shown at the top of the page, along with individual field [error messages](https://design-system.service.gov.uk/components/error-message/). This follows the GOV.UK Design System [validation pattern](https://design-system.service.gov.uk/patterns/validation/) and is built into the base page template.

### Flash messages

Messages created with Flask's `flash` function will be rendered using the GOV.UK Design System [notification banner component](https://design-system.service.gov.uk/components/notification-banner/). By default the blue "important" banner style will be used, unless a category of "success" is passed to use the green version.

### CSRF protection

Uses [Flask WTF](https://flask-wtf.readthedocs.io/en/stable/) to enable [Cross Site Request Forgery](https://en.wikipedia.org/wiki/Cross-site_request_forgery) protection per form and for the whole app.

CSRF errors are handled by creating a [flash message](#flash-messages) notification banner to inform the user that the form they submitted has expired.

### HTTP security headers

Uses [Flask Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) to set HTTP headers that can help protect against a few common web application security issues.

- Forces all connections to `https`, unless running with debug enabled.
- Enables [HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security).
- Sets Flask's session cookie to `secure`, so it will never be set if your application is somehow accessed via a non-secure connection.
- Sets Flask's session cookie to `httponly`, preventing JavaScript from being able to access its content.
- Sets [X-Frame-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options) to `SAMEORIGIN` to avoid [clickjacking](https://en.wikipedia.org/wiki/Clickjacking).
- Sets [X-XSS-Protection](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection) to enable a cross site scripting filter for IE and Safari (note Chrome has removed this and Firefox never supported it).
- Sets [X-Content-Type-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options) to prevent content type sniffing.
- Sets a strict [Referrer-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy) of `strict-origin-when-cross-origin` that governs which referrer information should be included with requests made.

### Content Security Policy

A strict default [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) (CSP) is set using [Flask Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) to mitigate [Cross Site Scripting](https://developer.mozilla.org/en-US/docs/Web/Security/Types_of_attacks#cross-site_scripting_xss) (XSS) and packet sniffing attacks. This prevents loading any resources that are not in the same domain as the application.

### Response compression

Uses [Flask Compress](https://github.com/colour-science/flask-compress) to compress response data. This inspects the `Accept-Encoding` request header, compresses using either gzip, deflate or brotli algorithms and sets the `Content-Encoding` response header. HTML, CSS, XML, JSON and JavaScript MIME types will all be compressed.

### Rate limiting

Uses [Flask Limiter](https://flask-limiter.readthedocs.io/en/stable/) to set request rate limits on routes. The default rate limit is 2 requests per second _and_ 60 requests per minute (whichever is hit first) based on the client's remote IP address. Every time a request exceeds the rate limit, the view function will not get called and instead a [HTTP 429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) status will be returned.

Rate limit storage can be backed by [Redis](https://redis.io/) using the `RATELIMIT_STORAGE_URL` config value in `config.py`, or fall back to in-memory if not present. Rate limit information will also be added to various [response headers](https://flask-limiter.readthedocs.io/en/stable/#rate-limiting-headers).

## Next steps

### Add your own blueprint

### Add database functionality

### Add user authentication

If you're implementing user authentication using [Flask Login](https://flask-login.readthedocs.io/en/latest/) you should also use a `key_func` to identify users on routes that require authentication, for example:

```python
@login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
```

This fixes the issue of rate limiting multiple users behind a single IP NAT or proxy, since the request is identified using a different unique value for each user.

### Deploy to Heroku
