#!/bin/bash

# InfraSense Real-Time Monitoring Startup Script
# This script starts the complete monitoring infrastructure

set -e

echo "🚀 Starting InfraSense Real-Time Monitoring Infrastructure"
echo "=========================================================="
echo ""

# Check if Docker is running
echo "🔍 Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Check if Docker Compose is available
echo "🔍 Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it first."
    exit 1
fi
echo "✅ Docker Compose is available"
echo ""

# Check if monitoring directory exists
echo "🔍 Checking monitoring directory..."
if [ ! -d "monitoring" ]; then
    echo "❌ Monitoring directory not found. Creating it..."
    mkdir -p monitoring
    echo "✅ Monitoring directory created"
fi
echo ""

# Check if required files exist
echo "🔍 Checking required files..."
REQUIRED_FILES=(
    "monitoring/docker-compose.yml"
    "monitoring/prometheus.yml"
    "monitoring/blackbox.yml"
    "monitoring/alert.rules.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file not found: $file"
        exit 1
    fi
done
echo "✅ All required files found"
echo ""

# Start monitoring services
echo "🚀 Starting monitoring services..."
cd monitoring || exit 1

echo "📦 Building Docker images..."
docker-compose build --no-cache
echo "✅ Docker images built"
echo ""

echo "📦 Starting containers..."
docker-compose up -d
echo "✅ Containers started"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30
echo ""

# Verify services are running
echo "🔍 Verifying services..."
SERVICES=(
    "prometheus"
    "node-exporter"
    "cadvisor"
    "postgres"
    "postgres-exporter"
    "blackbox-exporter"
    "customer-api"
    "payment-api"
    "auth-api"
    "backend"
    "frontend"
)

for service in "${SERVICES[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^$service$"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not running"
    fi
done
echo ""

# Check Prometheus targets
echo "🔍 Checking Prometheus targets..."
TARGETS=$(curl -s http://localhost:9090/api/v1/targets/metadata | jq -r '.data.activeTargets[] | .labels.instance')
if [ -z "$TARGETS" ]; then
    echo "❌ No Prometheus targets found"
else
    echo "✅ Prometheus targets found:"
    echo "$TARGETS" | while read -r target; do
        echo "   - $target"
    done
fi
echo ""

# Check application health
echo "🔍 Checking application health..."
HEALTH_CHECKS=(
    "http://localhost:3001/health"
    "http://localhost:3002/health"
    "http://localhost:3003/health"
    "http://localhost:8000/api/health"
)

for check in "${HEALTH_CHECKS[@]}"; do
    if curl -s "$check" | grep -q "healthy"; then
        echo "✅ $(echo "$check" | cut -d'/' -f3) is healthy"
    else
        echo "❌ $(echo "$check" | cut -d'/' -f3) is not healthy"
    fi
done
echo ""

# Display monitoring dashboard URLs
echo "🎯 Monitoring Dashboard URLs:"
echo "   - Prometheus: http://localhost:9090"
echo "   - Customer API: http://localhost:3001"
echo "   - Payment API: http://localhost:3002"
echo "   - Auth API: http://localhost:3003"
echo "   - Backend API: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo ""

echo "✅ InfraSense Real-Time Monitoring Infrastructure is ready!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Monitor real-time metrics in the dashboard"
echo "3. Check alerts and predictions"
echo "4. Explore component details and correlations"
echo ""
echo "For troubleshooting, run: docker logs <container_name>"
echo "For status, run: docker ps"
echo "For metrics, run: curl http://localhost:9090/metrics"
echo ""
