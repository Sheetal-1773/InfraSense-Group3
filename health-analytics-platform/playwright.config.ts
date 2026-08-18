import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5174',
    trace: 'on-first-retry',
  },
  webServer: [
    {
      command: 'python -m uvicorn app.main:app --host 127.0.0.1 --port 8001',
      url: 'http://127.0.0.1:8001/api/health',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
      cwd: './backend',
      env: {
        DATABASE_URL: 'sqlite:///./infrasense_e2e.db',
        DATA_MODE: 'mock',
        ENABLE_SEED_DATA: 'true',
        ENABLE_REAL_COLLECTION: 'false',
        SIMULATOR_ENABLED: 'true',
        ENABLE_ANOMALY_DETECTION: 'true',
        ENABLE_PREDICTION: 'true',
        ENABLE_CORRELATION: 'true',
        ENABLE_EMAIL_NOTIFICATIONS: 'false',
      },
    },
    {
      command: 'npm run dev',
      url: 'http://localhost:5174',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
      env: {
        VITE_API_PROXY: 'http://127.0.0.1:8001',
      },
    },
  ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})