module.exports = {
  title: "Eurydice",
  baseURL: "/api/v1",
  version: process.env.VUE_APP_VERSION || "development",
  releaseCycle: "Alpha",
  refreshIntervalInMs: 5 * 1000,
  serverDownIntervalInMs: 3 * 60 * 1000, // 3 min
  transferablesPerPage: 10,
};
