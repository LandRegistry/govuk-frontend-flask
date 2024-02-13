# Remove existing GOV.UK Frontend assets
rm -rf app/static/fonts
rm -rf app/static/images
rm -rf app/static/govuk-frontend*

# Get new release distribution assets and move to static directory
curl -L https://github.com/alphagov/govuk-frontend/releases/download/v5.1.0/release-v5.1.0.zip > govuk_frontend.zip
unzip -o govuk_frontend.zip -d app/static
mv app/static/assets/* app/static

# Tidy up
rm -rf app/static/assets
rm -rf app/static/VERSION.txt
rm -rf govuk_frontend.zip

#####################################################################
## The following is only required for the demos and can be removed ##
#####################################################################

# Remove existing GOV.UK Frontend test fixtures
rm -rf govuk_components

# Get new release source code and move to a directory
curl -L https://github.com/alphagov/govuk-frontend/archive/refs/tags/v5.1.0.zip > govuk_frontend_source.zip
unzip -o govuk_frontend_source.zip -d govuk_frontend_source
mkdir govuk_components
mv govuk_frontend_source/govuk-frontend-5.1.0/packages/govuk-frontend/src/govuk/components/** govuk_components

# Remove all files apart from test fixtures
find govuk_components -type f ! -name '*.yaml' -delete

# Tidy up
rm -rf govuk_frontend_source
rm -rf govuk_frontend_source.zip
