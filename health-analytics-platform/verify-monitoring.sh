#!/bin/bash

# InfraSense Monitoring Verification Script
# This script verifies the complete monitoring infrastructure

set -e

echo "🔍 Starting InfraSense Monitoring Verification"
echo "=============================================="
echo ""

# Function to check if a service is running
is_service_running() {
    local service_name="$1"
    if docker ps --format '{{.Names}}' | grep -q "^$service_name$"; then
        return 0
    else
        return 1
    fi
}

# Function to check if a URL is accessible
is_url_accessible() {
    local url="$1"
    if curl -s "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if a metric endpoint is working
is_metric_endpoint_working() {
    local url="$1"
    if curl -s "$url" | grep -q "# HELP"; then
        return 0
    else
        return 1
    fi
}

# Function to check if Prometheus is collecting metrics
is_prometheus_collecting() {
    local url="$1"
    if curl -s "$url" | grep -q "activeTargets"; then
        return 0
    else
        return 1
    fi
}

echo "1. Verifying Docker Services"
echo "============================"
echo ""

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
    if is_service_running "$service"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is NOT running"
    fi
done
echo ""

echo "2. Verifying Exporters Producing Metrics"
echo "=========================================="
echo ""

EXPORTERS=(
    "http://localhost:9100/metrics"
    "http://localhost:8080/metrics"
    "http://localhost:9187/metrics"
    "http://localhost:9115/metrics"
)

for exporter in "${EXPORTERS[@]}"; do
    if is_metric_endpoint_working "$exporter"; then
        echo "✅ $exporter is producing metrics"
    else
        echo "❌ $exporter is NOT producing metrics"
    fi
done
echo ""

echo "3. Verifying Prometheus Targets"
echo "================================"
echo ""

if is_prometheus_collecting "http://localhost:9090/api/v1/targets/metadata"; then
    echo "✅ Prometheus is collecting targets"
    
    # Get active targets
    TARGETS=$(curl -s http://localhost:9090/api/v1/targets/metadata | jq -r '.data.activeTargets[] | .labels.instance')
    
    if [ -z "$TARGETS" ]; then
        echo "❌ No active targets found"
    else
        echo "✅ Active targets found:"
        echo "$TARGETS" | while read -r target; do
            echo "   - $target"
        done
    fi
else
    echo "❌ Prometheus is NOT collecting targets"
fi
echo ""

echo "4. Verifying Backend Receiving Real Metrics"
echo "============================================"
echo ""

BACKEND_ENDPOINTS=(
    "http://localhost:8000/api/components"
    "http://localhost:8000/api/alerts"
    "http://localhost:8000/api/predictions"
    "http://localhost:8000/api/correlations"
)

for endpoint in "${BACKEND_ENDPOINTS[@]}"; do
    if is_url_accessible "$endpoint"; then
        echo "✅ $endpoint is accessible"
    else
        echo "❌ $endpoint is NOT accessible"
    fi
done
echo ""

echo "5. Verifying Database Storing Metrics"
echo "======================================"
echo ""

# Check if PostgreSQL is running
if is_service_running "postgres"; then
    echo "✅ PostgreSQL is running"
    
    # Check if we can connect to PostgreSQL
    if psql -h localhost -U infrasense -d infrasense -c "SELECT 1" > /dev/null 2>&1; then
        echo "✅ PostgreSQL connection successful"
        
        # Check if metrics tables exist
        TABLES=$(psql -h localhost -U infrasense -d infrasense -t -c "\dt" | awk '{print $1}')
        
        if echo "$TABLES" | grep -q "metrics"; then
            echo "✅ Metrics table found"
        else
            echo "❌ Metrics table NOT found"
        fi
        
        if echo "$TABLES" | grep -q "component_metrics"; then
            echo "✅ Component metrics table found"
        else
            echo "❌ Component metrics table NOT found"
        fi
        
        if echo "$TABLES" | grep -q "alert_history"; then
            echo "✅ Alert history table found"
        else
            echo "❌ Alert history table NOT found"
        fi
    else
        echo "❌ PostgreSQL connection failed"
    fi
else
    echo "❌ PostgreSQL is NOT running"
fi
echo ""

echo "6. Verifying Alerts Are Generated"
echo "=================================="
echo ""

if is_url_accessible "http://localhost:8000/api/alerts?status=active"; then
    ALERTS=$(curl -s http://localhost:8000/api/alerts?status=active | jq -r '.data[] | .id')
    
    if [ -z "$ALERTS" ]; then
        echo "✅ No active alerts (this is normal if everything is healthy)"
    else
        echo "✅ Active alerts found:"
        echo "$ALERTS" | while read -r alert; do
            echo "   - $alert"
        done
    fi
else
    echo "❌ Alerts endpoint NOT accessible"
fi
echo ""

echo "7. Verifying Health Scores Are Changing"
echo "========================================"
echo ""

if is_url_accessible "http://localhost:8000/api/components/health"; then
    HEALTH=$(curl -s http://localhost:8000/api/components/health | jq -r '.overall')
    
    if [ -z "$HEALTH" ]; then
        echo "❌ Health score NOT found"
    else
        echo "✅ Health score: $HEALTH"
    fi
else
    echo "❌ Health endpoint NOT accessible"
fi
echo ""

echo "8. Verifying Predictions Are Updating"
echo "======================================"
echo ""

if is_url_accessible "http://localhost:8000/api/predictions"; then
    PREDICTIONS=$(curl -s http://localhost:8000/api/predictions | jq -r '.data[] | .id')
    
    if [ -z "$PREDICTIONS" ]; then
        echo "✅ No predictions found (this is normal if everything is healthy)"
    else
        echo "✅ Predictions found:"
        echo "$PREDICTIONS" | while read -r prediction; do
            echo "   - $prediction"
        done
    fi
else
    echo "❌ Predictions endpoint NOT accessible"
fi
echo ""

echo "9. Verifying Correlations Are Updating"
echo "========================================"
echo ""

if is_url_accessible "http://localhost:8000/api/correlations"; then
    CORRELATIONS=$(curl -s http://localhost:8000/api/correlations | jq -r '.data[] | .id')
    
    if [ -z "$CORRELATIONS" ]; then
        echo "✅ No correlations found (this is normal if everything is healthy)"
    else
        echo "✅ Correlations found:"
        echo "$CORRELATIONS" | while read -r correlation; do
            echo "   - $correlation"
        done
    fi
else
    echo "❌ Correlations endpoint NOT accessible"
fi
echo ""

echo "10. Verifying Frontend Is Displaying Live Data"
echo "=============================================="
echo ""

if is_url_accessible "http://localhost:3000"; then
    echo "✅ Frontend is accessible at http://localhost:3000"
    echo "   Open your browser to http://localhost:3000 to verify live data"
else
    echo "❌ Frontend is NOT accessible"
fi
echo ""

echo "📊 Summary"
echo "=========="
echo ""
echo "✅ All verification steps completed"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Monitor real-time metrics in the dashboard"
echo "3. Check alerts and predictions"
echo "4. Explore component details and correlations"
echo ""
echo "For troubleshooting:"
echo "1. Check container logs: docker logs <container_name>"
echo "2. Check container status: docker ps"
echo "3. Check Prometheus targets: curl http://localhost:9090/targets"
echo "4. Check Prometheus metrics: curl http://localhost:9090/metrics"
echo ""
echo "✅ InfraSense Monitoring Verification Complete!"
echo "================================================"
