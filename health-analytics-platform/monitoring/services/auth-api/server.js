const express = require('express');
const promClient = require('prom-client');
const bodyParser = require('body-parser');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

// Create Express app
const app = express();
const port = process.env.PORT || 3000;
const metricsPort = process.env.METRICS_PORT || 9093;

// Middleware
app.use(cors());
app.use(helmet());
app.use(morgan('combined'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Prometheus Metrics Setup
const collectDefaultMetrics = promClient.collectDefaultMetrics;
collectDefaultMetrics({ timeout: 5000 });

// Custom metrics
const httpRequestDurationMicroseconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5, 10]
});

const httpRequestCount = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const httpRequestErrors = new promClient.Counter({
  name: 'http_request_errors_total',
  help: 'Total HTTP request errors',
  labelNames: ['method', 'route', 'status_code']
});

const apiResponseTime = new promClient.Gauge({
  name: 'api_response_time_seconds',
  help: 'Current API response time',
  labelNames: ['endpoint']
});

const apiErrorRate = new promClient.Gauge({
  name: 'api_error_rate',
  help: 'Current API error rate',
  labelNames: ['endpoint']
});

const apiAvailability = new promClient.Gauge({
  name: 'api_availability',
  help: 'Current API availability',
  labelNames: ['endpoint']
});

const apiThroughput = new promClient.Counter({
  name: 'api_throughput_requests',
  help: 'API throughput requests',
  labelNames: ['endpoint']
});

const apiLatency = new promClient.Histogram({
  name: 'api_latency_seconds',
  help: 'API latency in seconds',
  labelNames: ['endpoint'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', promClient.register.contentType);
    const metrics = await promClient.register.metrics();
    res.end(metrics);
  } catch (err) {
    res.status(500).end(err);
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', service: 'auth-api' });
});

// API endpoints with metrics
app.post('/api/auth/login', async (req, res) => {
  const start = Date.now();
  
  try {
    // Simulate some processing time
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Simulate occasional errors
    if (Math.random() < 0.02) {
      throw new Error('Simulated error');
    }
    
    const responseTime = (Date.now() - start) / 1000;
    
    // Update metrics
    httpRequestDurationMicroseconds.observe({ method: 'POST', route: '/api/auth/login', status_code: 200 }, responseTime);
    httpRequestCount.inc({ method: 'POST', route: '/api/auth/login', status_code: 200 });
    apiResponseTime.set({ endpoint: '/api/auth/login' }, responseTime);
    apiThroughput.inc({ endpoint: '/api/auth/login' });
    apiLatency.observe({ endpoint: '/api/auth/login' }, responseTime);
    
    res.status(200).json({ token: 'sample-token', user_id: 1, username: 'john.doe' });
    
  } catch (error) {
    const responseTime = (Date.now() - start) / 1000;
    httpRequestDurationMicroseconds.observe({ method: 'POST', route: '/api/auth/login', status_code: 500 }, responseTime);
    httpRequestCount.inc({ method: 'POST', route: '/api/auth/login', status_code: 500 });
    httpRequestErrors.inc({ method: 'POST', route: '/api/auth/login', status_code: 500 });
    apiResponseTime.set({ endpoint: '/api/auth/login' }, responseTime);
    apiErrorRate.set({ endpoint: '/api/auth/login' }, 0.05);
    apiAvailability.set({ endpoint: '/api/auth/login' }, 0.95);
    
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/auth/register', async (req, res) => {
  const start = Date.now();
  
  try {
    // Simulate some processing time
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Simulate occasional errors
    if (Math.random() < 0.01) {
      throw new Error('Simulated error');
    }
    
    const responseTime = (Date.now() - start) / 1000;
    
    // Update metrics
    httpRequestDurationMicroseconds.observe({ method: 'POST', route: '/api/auth/register', status_code: 201 }, responseTime);
    httpRequestCount.inc({ method: 'POST', route: '/api/auth/register', status_code: 201 });
    apiResponseTime.set({ endpoint: '/api/auth/register' }, responseTime);
    apiThroughput.inc({ endpoint: '/api/auth/register' });
    apiLatency.observe({ endpoint: '/api/auth/register' }, responseTime);
    
    res.status(201).json({ user_id: 2, username: req.body.username, email: req.body.email });
    
  } catch (error) {
    const responseTime = (Date.now() - start) / 1000;
    httpRequestDurationMicroseconds.observe({ method: 'POST', route: '/api/auth/register', status_code: 500 }, responseTime);
    httpRequestCount.inc({ method: 'POST', route: '/api/auth/register', status_code: 500 });
    httpRequestErrors.inc({ method: 'POST', route: '/api/auth/register', status_code: 500 });
    apiResponseTime.set({ endpoint: '/api/auth/register' }, responseTime);
    apiErrorRate.set({ endpoint: '/api/auth/register' }, 0.03);
    apiAvailability.set({ endpoint: '/api/auth/register' }, 0.97);
    
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/auth/validate', async (req, res) => {
  const start = Date.now();
  
  try {
    // Simulate some processing time
    await new Promise(resolve => setTimeout(resolve, 50));
    
    // Simulate occasional errors
    if (Math.random() < 0.01) {
      throw new Error('Simulated error');
    }
    
    const responseTime = (Date.now() - start) / 1000;
    
    // Update metrics
    httpRequestDurationMicroseconds.observe({ method: 'GET', route: '/api/auth/validate', status_code: 200 }, responseTime);
    httpRequestCount.inc({ method: 'GET', route: '/api/auth/validate', status_code: 200 });
    apiResponseTime.set({ endpoint: '/api/auth/validate' }, responseTime);
    apiThroughput.inc({ endpoint: '/api/auth/validate' });
    apiLatency.observe({ endpoint: '/api/auth/validate' }, responseTime);
    
    res.status(200).json({ valid: true, user_id: 1, username: 'john.doe' });
    
  } catch (error) {
    const responseTime = (Date.now() - start) / 1000;
    httpRequestDurationMicroseconds.observe({ method: 'GET', route: '/api/auth/validate', status_code: 500 }, responseTime);
    httpRequestCount.inc({ method: 'GET', route: '/api/auth/validate', status_code: 500 });
    httpRequestErrors.inc({ method: 'GET', route: '/api/auth/validate', status_code: 500 });
    apiResponseTime.set({ endpoint: '/api/auth/validate' }, responseTime);
    apiErrorRate.set({ endpoint: '/api/auth/validate' }, 0.02);
    apiAvailability.set({ endpoint: '/api/auth/validate' }, 0.98);
    
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start the main server
app.listen(port, () => {
  console.log(`Auth API running on port ${port}`);
});

// Start the metrics server
const metricsServer = express();
metricsServer.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', promClient.register.contentType);
    const metrics = await promClient.register.metrics();
    res.end(metrics);
  } catch (err) {
    res.status(500).end(err);
  }
});

metricsServer.listen(metricsPort, () => {
  console.log(`Metrics server running on port ${metricsPort}`);
});