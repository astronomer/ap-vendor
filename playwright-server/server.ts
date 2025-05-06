const { chromium } = require("playwright");

(async () => {
  const browserServer = await chromium.launchServer({
    port: 9222,
    wsPath: "ws",
    logger: {
      isEnabled: (name, severity) => true,
      log: (name, severity, message, args) => console.log(`${name} ${message}`)
    }
  });
  const wsEndpoint = browserServer.wsEndpoint();
  console.log("Listening on: ", wsEndpoint);
})();
