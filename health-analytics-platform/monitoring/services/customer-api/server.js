const express = require('express');
const promClient = require('prom-client');
const axios = require('axios');
const bodyParser = require('body-parser');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

// Create Express app
const app = express();
const port = process.env.PORT || 3000;
const metricsPort = process.env.METRICS_PORT || 9091;

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

const apiErrorRateGauge = new promClient.Gauge({
  name: 'api_error_rate_gauge',
  help: 'Current API error rate gauge',
  labelNames: ['endpoint']
});

const apiAvailabilityGauge = new promClient.Gauge({
  name: 'api_availability_gauge',
  help: 'Current API availability gauge',
  labelNames: ['endpoint']
});

const apiResponseTimeGauge = new promClient.Gauge({
  name: 'api_response_time_gauge',
  help: 'Current API response time gauge',
  labelNames: ['endpoint']
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
  res.status(200).json({ status: 'healthy', service: 'customer-api' });
});

// API endpoints with metrics
app.get('/api/customers', async (req, res) => {
  const start = Date.now();
  
  try {
    // Simulate some processing time
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Simulate occasional errors
    if (Math.random() < 0.05) {
      throw new Error('Simulated error');
    }
    
    const responseTime = (Date.now() - start) / 1000;
    
    // Update metrics
    httpRequestDurationMicroseconds.observe({ method: 'GET', route: '/api/customers', status_code: 200 }, responseTime);
    httpRequestCount.inc({ method: 'GET', route: '/api/customers', status_code: 200 });
    apiResponseTime.set({ endpoint: '/api/customers' }, responseTime);
    apiThroughput.inc({ endpoint: '/api/customers' });
    apiLatency.observe({ endpoint: '/api/customers' }, responseTime);
    
    res.status(200).json({
      customers: [
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
      ]
    });
    
  } catch (error) {
    const responseTime = (Date.now() - start) / 1000;
    httpRequestDurationMicroseconds.observe({ method: 'GET', route: '/api/customers', status_code: 500 }, responseTime);
    httpRequestCount.inc({ method: 'GET', route: '/api/customers', status_code: 500 });
    httpRequestErrors.inc({ method: 'GET', route: '/api/customers', status_code: 500 });
    apiResponseTime.set({ endpoint: '/api/customers' }, responseTime);
    apiErrorRate.set({ endpoint: '/api/customers' }, 0.1);
    apiAvailability.set({ endpoint: '/api/customers' }, 0.9);
    
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/customers', async (req, res) => {
  const start = Date.now();
  
  try {
    // Simulate some processing time
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Simulate occasional errors
    if (Math.random() < 0.02) {
      throw new Error('Simulated error');
    }
    
    const responseTime = (Date.now() - start) / 1000;
    
    // Update metrics
    httpRequestDurationMicroseconds.observe({ method: 'POST', route: '/api/customers', status_code: 201 }, responseTime);
    httpRequestCount.inc({ method: 'POST', route: '/api/customers', status_code: 201 });
    apiResponseTime.set({ endpoint: '/api/customers' }, responseTime);
    apiThroughput.inc({ endpoint: '/api/customers' });
    apiLatency.observe({ endpoint: '/api/customers' }, responseTime);
    
    res.status(201).json({ id: 3, name: req.body.name, email: req.body.email });
    
  } catch (error) {
    const responseTime = (Date.now() - start) / 1000;
    httpRequestDurationMicroseconds.observe({ method: 'POST', route: '/api/customers', status_code: 500 }, responseTime);
    httpRequestCount.inc({ method: 'POST', route: '/api/customers', status_code: 500 });
    httpRequestErrors.inc({ method: 'POST', route: '/api/customers', status_code: 500 });
    apiResponseTime.set({ endpoint: '/api/customers' }, responseTime);
    apiErrorRate.set({ endpoint: '/api/customers' }, 0.05);
    apiAvailability.set({ endpoint: '/api/customers' }, 0.95);
    
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/customers/:id', async (req, res) => {
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
    httpRequestDurationMicroseconds.observe({ method: 'GET', route: '/api/customers/:id', status_code: 200 }, responseTime);
    httpRequestCount.inc({ method: 'GET', route: '/api/customers/:id', status_code: 200 });
    apiResponseTime.set({ endpoint: '/api/customers/:id' }, responseTime);
    apiThroughput.inc({ endpoint: '/api/customers/:id' });
    apiLatency.observe({ endpoint: '/api/customers/:id' }, responseTime);
    
    res.status(200).json({ id: req.params.id, name: 'John Doe', email: 'john@example.com' });
    
  } catch (error) {
    const responseTime = (Date.now() - start) / 1000;
    httpRequestDurationMicroseconds.observe({ method: 'GET', route: '/api/customers/:id', status_code: 500 }, responseTime);
    httpRequestCount.inc({ method: 'GET', route: '/api/customers/:id', status_code: 500 });
    httpRequestErrors.inc({ method: 'GET', route: '/api/customers/:id', status_code: 500 });
    apiResponseTime.set({ endpoint: '/api/customers/:id' }, responseTime);
    apiErrorRate.set({ endpoint: '/api/customers/:id' }, 0.02);
    apiAvailability.set({ endpoint: '/api/customers/:id' }, 0.98);
    
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start metrics server
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

// Start the main server
app.listen(port, () => {
  console.log(`Customer API running on port ${port}`);
});

// Start the metrics server
metricsServer.listen(metricsPort, () => {
  console.log(`Metrics server running on port ${metricsPort}`);
});