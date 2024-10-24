const path = require("path");

function resolve(dir) {
  return path.join(__dirname, dir);
}

const WEBPACK_CONFIGURATION = {
  resolve: {
    extensions: [".js", ".vue"],
    alias: {
      "@common": resolve("src/common"),
      "@destination": resolve("src/destination"),
      "@origin": resolve("src/origin"),
    },
  },
};

const PERMISSIONS_POLICY =
  "accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), camera=(), cross-origin-isolated=(), display-capture=(), document-domain=(), encrypted-media=(), execution-while-not-rendered=(), execution-while-out-of-viewport=(), fullscreen=(), geolocation=(), gyroscope=(), keyboard-map=(), magnetometer=(), microphone=(), midi=(), navigation-override=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), usb=(), web-share=(), xr-spatial-tracking=(), interest-cohort=()";

// NOTE: script-src unsafe-eval should NOT be set in production
const CONTENT_SECURITY_POLICY =
  "default-src 'none'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'";

const REFERRER_POLICY = "same-origin";

const X_CONTENT_TYPE_OPTIONS = "nosniff";
module.exports = {
  devServer: {
    allowedHosts: ["origin.localhost", "destination.localhost"],
    overlay: false,
    headers: {
      // NOTE: this is only for the development environment, production headers
      //       should be set in the production webserver's configuration
      "Permissions-Policy": PERMISSIONS_POLICY,
      "Content-Security-Policy": CONTENT_SECURITY_POLICY,
      "Referrer-Policy": REFERRER_POLICY,
      "X-Content-Type-Options": X_CONTENT_TYPE_OPTIONS,
    },
  },
  transpileDependencies: ["vuetify"],
  productionSourceMap: process.env.NODE_ENV !== "production",
  configureWebpack: WEBPACK_CONFIGURATION,
  chainWebpack: (config) => {
    // disable splitting manifest to have more restrictive CSP
    // this allows for no unsafe-inline in CSP
    // https://github.com/vuejs/vue-cli/issues/1074
    config.plugins.delete("split-manifest").delete("inline-manifest");
  },
};
