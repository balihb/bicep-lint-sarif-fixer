// https://docs.renovatebot.com/configuration-options/

module.exports = {
    configMigration: true,
    dependencyDashboardOSVVulnerabilitySummary: 'all',
    fetchChangeLogs: 'on',
    onboarding: true,
    onboardingConfigFileName: "renovate.json5",
    osvVulnerabilityAlerts: true,
    platform: "github",
    repositories: ["balihb/bicep-lint-sarif-fixer"],
};
