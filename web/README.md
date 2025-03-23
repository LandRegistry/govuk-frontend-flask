# Building static assets

Use [Webpack](https://webpack.js.org/) to bundle JavaScript, SCSS, images, and fonts, while optimising the output for performance. It uses various loaders and plugins to process files and generate the final build:

- [**CSS Minimizer Webpack Plugin**](https://webpack.js.org/plugins/css-minimizer-webpack-plugin/): Minimises the CSS output to reduce file size and improve page load times.
- [**PostCSS Preset Env**](https://github.com/csstools/postcss-plugins/tree/main/plugin-packs/postcss-preset-env): Uses [Autoprefixer](https://github.com/postcss/autoprefixer) to add vendor prefixes and ensure compatibility with older browsers.
- [**Babel Preset Env**](https://babeljs.io/docs/babel-preset-env): Transpiles ES6+ JavaScript for cross-browser compatibility while allowing the use of modern JavaScript features.
- [**Copy Webpack Plugin**](https://webpack.js.org/plugins/copy-webpack-plugin/): Automates copying images and fonts from [GOV.UK Frontend](https://frontend.design-system.service.gov.uk/) to the output directory.
- [**Webpack Dev Server**](https://webpack.js.org/configuration/dev-server/): Serves files from the output directory with live reloading for development workflows.

## Prerequisites

- [Node Version Manager (nvm)](https://github.com/nvm-sh/nvm)

## Get started

1. Install the correct version of [Node.js](https://nodejs.org/en). This is determined by the `.nvmrc` file and is typically the latest LTS release codename.

   ```shell
   nvm install
   ```

2. Install the Node package dependencies from [npm](https://www.npmjs.com/):

   ```shell
   npm install
   ```

## How to

### Use GOV.UK Design System components

The `main.scss` file at `/web/src/scss` is highly selective about which `components` are imported above the required `base`, `core`, `objects`, `utilities` and `overrides`. Components account for around 70% of the output CSS, so should only be included if they are used in the service, in order to keep distributon file sizes small.

By default, the following components styling is imported, because they are used in the template app:

- [Back link](https://design-system.service.gov.uk/components/back-link/)
- [Button](https://design-system.service.gov.uk/components/button/)
- [Cookie banner](https://design-system.service.gov.uk/components/cookie-banner/)
- [Error summary](https://design-system.service.gov.uk/components/error-summary/)
- [Footer](https://design-system.service.gov.uk/components/footer/)
- [Header](https://design-system.service.gov.uk/components/header/)
- [Notification banner](https://design-system.service.gov.uk/components/notification-banner/)
- [Phase banner](https://design-system.service.gov.uk/components/phase-banner/)
- [Radios](https://design-system.service.gov.uk/components/radios/)
- [Service navigation](https://design-system.service.gov.uk/components/service-navigation/)
- [Skip link](https://design-system.service.gov.uk/components/skip-link/)
- [Table](https://design-system.service.gov.uk/components/table/)

Simply comment out, or uncomment, any other components in `main.scss` that you need to exclude or include.

The same approach applies to JS; the `govuk-frontend.mjs` file at `/web/src/js/modules` only imports and creates the components that are used:

- Button
- Error summary
- Notification banner
- Radios
- Service navigation
- Skip link

> **Note**: Although there is JS for the Header component, this is not needed when using the newer Service navigation component alongside it. If you're not using the Service navigation component, remove its JS import and replace it with the Header's.

For comparison (using GOV.UK Frontend v5.9.0):

| Asset         | Size (KB) |
| ------------- | --------- |
| All CSS       | 122       |
| Selective CSS | 75 (-38%) |
| All JS        | 46        |
| Selective JS  | 11 (-76%) |

### Format source code

Use [Prettier](https://prettier.io/), an opinionated code formatter, for consistency:

```shell
npm run format
```

### Build assets

Output compiled CSS, JS, fonts and images to `./dist`:

```shell
npm run build
```

### Watch changes

Rebuild distribution assets automatically when source is changed:

```shell
npm run watch
```

### Update dependencies

To update Node package dependencies (such as [govuk-frontend](https://www.npmjs.com/package/govuk-frontend)), use [npm-check-updates](https://www.npmjs.com/package/npm-check-updates):

```shell
ncu -u
```

If you want to be more cautious you can check only for patch or minor level updates:

```shell
ncu --target patch -u
```

```shell
ncu --target minor -u
```
