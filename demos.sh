# Remove existing GOV.UK Frontend test fixtures
rm -rf app/demos/govuk_components

# Get new release source code and move to a directory
curl -L https://github.com/alphagov/govuk-frontend/archive/refs/tags/v5.8.0.zip > govuk_frontend_source.zip
unzip -o govuk_frontend_source.zip -d govuk_frontend_source
mkdir app/demos/govuk_components
mv govuk_frontend_source/govuk-frontend-5.8.0/packages/govuk-frontend/src/govuk/components/** app/demos/govuk_components

# Remove all files apart from test fixtures
find app/demos/govuk_components -type f ! -name '*.yaml' -delete

# Tidy up
rm -rf govuk_frontend_source
rm -rf govuk_frontend_source.zip
