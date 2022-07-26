# Remove existing GOV.UK Frontend assets
rm -rf app/static/fonts
rm -rf app/static/images
rm -rf app/static/govuk-frontend*

# Get new release distribution assets and move to static directory
curl -L https://github.com/alphagov/govuk-frontend/releases/download/v4.2.0/release-v4.2.0.zip > govuk_frontend.zip
unzip -o govuk_frontend.zip -d app/static
mv app/static/assets/* app/static

# Tidy up
rm -rf app/static/assets
rm -rf app/static/VERSION.txt
rm -rf govuk_frontend.zip