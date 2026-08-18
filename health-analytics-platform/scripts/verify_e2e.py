#!/usr/bin/env python3
"""
InfraSense End-to-End Verification Script

Tests the complete data pipeline:
Docker Services → Backend → Database → Prometheus → Component Discovery → Metrics → WebSocket → Dashboard

Usage:
    python scripts/verify_e2e.py
    python scripts/verify_e2e.py --verbose
    python scripts/verify_e2e.py --skip-docker
"""

import argparse
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import psycopg2

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class E2EVerifier:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[Dict] = []
        self.base_url = "http://localhost:8000"
        
    def log(self, message: str, level: str = "INFO"):
        if self.verbose or level in ["PASS", "FAIL", "ERROR"]:
            prefix = {
                "INFO": f"{Colors.BLUE}[INFO]{Colors.RESET}",
                "PASS": f"{Colors.GREEN}[PASS]{Colors.RESET}",
                "FAIL": f"{Colors.RED}[FAIL]{Colors.RESET}",
                "WARN": f"{Colors.YELLOW}[WARN]{Colors.RESET}",
                "ERROR": f"{Colors.RED}[ERROR]{Colors.RESET}",
            }.get(level, "[INFO]")
            print(f"{prefix} {message}")

    def check(self, name: str, check_func, expected: str = None) -> bool:
        """Run a check and record the result."""
        self.log(f"Checking: {name}...", "INFO")
        try:
            result, message = check_func()
            success = bool(result)
            
            status = "PASS" if success else "FAIL"
            self.log(f"{name}: {message}", status)
            
            self.results.append({
                "name": name,
                "success": success,
                "message": message,
                "expected": expected,
                "timestamp": datetime.utcnow().isoformat()
            })
            return success
        except Exception as e:
            self.log(f"{name}: {str(e)}", "ERROR")
            self.results.append({
                "name": name,
                "success": False,
                "message": f"Exception: {str(e)}",
                "expected": expected,
                "timestamp": datetime.utcnow().isoformat()
            })
            return False

    # =========================================================================
    # Individual Checks
    # =========================================================================
    
    def check_docker_services(self) -> Tuple[bool, str]:
        """Check if Docker services are running."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            running_containers = result.stdout.strip().split('\n')
            running_containers = [c for c in running_containers if c]
            
            required_services = ['postgres', 'backend']
            missing = [s for s in required_services if not any(s in c for c in running_containers)]
            
            if missing:
                return False, f"Missing services: {', '.join(missing)}. Running: {', '.join(running_containers) or 'none'}"
            
            return True, f"All required services running: {', '.join(running_containers)}"
        except FileNotFoundError:
            return False, "Docker not found. Is Docker installed? Run: docker compose up -d"
        except Exception as e:
            return False, f"Docker error: {str(e)}"

    def check_backend_health(self) -> Tuple[bool, str]:
        """Check if backend is healthy."""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return True, f"Backend healthy. Mode: {data.get('data_mode', 'unknown')}, Service: {data.get('service', 'unknown')}"
            return False, f"Backend returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to backend. Is it running on port 8000?"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def check_database_connection(self) -> Tuple[bool, str]:
        """Check TimescaleDB/PostgreSQL connection."""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="infrasense",
                password="infrasense",
                dbname="infrasense",
                connect_timeout=5
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return True, f"Database connected. PostgreSQL version: {version[:50]}..."
        except psycopg2.OperationalError as e:
            return False, f"Cannot connect to database: {str(e)[:100]}"
        except Exception as e:
            return False, f"Database error: {str(e)}"

    def check_database_tables(self) -> Tuple[bool, str]:
        """Check if required tables exist."""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="infrasense",
                password="infrasense",
                dbname="infrasense",
                connect_timeout=5
            )
            cursor = conn.cursor()
            
            required_tables = ['components', 'categories', 'alerts', 'predictions', 'component_metrics']
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing = [t for t in required_tables if t not in existing_tables]
            
            cursor.close()
            conn.close()
            
            if missing:
                return False, f"Missing tables: {', '.join(missing)}"
            return True, f"All required tables exist: {', '.join(existing_tables)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def check_component_discovery(self) -> Tuple[bool, str]:
        """Check component discovery API."""
        try:
            response = requests.get(f"{self.base_url}/api/components/discover", timeout=10)
            if response.status_code != 200:
                return False, f"API returned status {response.status_code}"
            
            data = response.json()
            discovered = data.get("discovered", 0)
            components = data.get("components", [])
            
            if discovered == 0:
                return False, "No components discovered. Check Prometheus connection and data source configuration."
            
            # Group by type
            by_type = {}
            for c in components:
                t = c.get("type", "unknown")
                by_type[t] = by_type.get(t, 0) + 1
            
            type_str = ", ".join([f"{k}: {v}" for k, v in by_type.items()])
            return True, f"Discovered {discovered} components. Types: {type_str}"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to backend"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def check_infrastructure_summary(self) -> Tuple[bool, str]:
        """Check infrastructure summary API."""
        try:
            response = requests.get(f"{self.base_url}/api/components/infrastructure/summary", timeout=10)
            if response.status_code != 200:
                return False, f"API returned status {response.status_code}"
            
            data = response.json()
            total = data.get("total", 0)
            by_type = data.get("by_type", {})
            by_status = data.get("by_status", {})
            
            if total == 0:
                return False, "No components in database. Run component discovery first."
            
            return True, f"Total: {total} components. Types: {by_type}. Status: {by_status}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def check_metrics_ingestion(self) -> Tuple[bool, str]:
        """Check if metrics are being ingested."""
        try:
            # Check if components have metrics
            response = requests.get(f"{self.base_url}/api/components", timeout=10)
            if response.status_code != 200:
                return False, f"Components API returned {response.status_code}"
            
            data = response.json()
            components = data.get("data", [])
            
            if not components:
                return False, "No components in database"
            
            # Check for recent metrics in database
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="infrasense",
                password="infrasense",
                dbname="infrasense",
                connect_timeout=5
            )
            cursor = conn.cursor()
            
            # Check component_metrics table
            cursor.execute("SELECT COUNT(*) FROM component_metrics")
            metric_count = cursor.fetchone()[0]
            
            # Check for recent metrics (last 5 minutes)
            cursor.execute("""
                SELECT COUNT(*) FROM component_metrics 
                WHERE timestamp > NOW() - INTERVAL '5 minutes'
            """)
            recent_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            if metric_count == 0:
                return False, "No metrics in database. Metrics pipeline may not be working."
            
            if recent_count == 0:
                return False, f"Found {metric_count} total metrics but none in last 5 minutes. Data may be stale."
            
            return True, f"Metrics pipeline working. {recent_count} recent metrics, {metric_count} total."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def check_websocket(self) -> Tuple[bool, str]:
        """Check WebSocket connectivity."""
        if not WEBSOCKET_AVAILABLE:
            return False, "websocket-client library not installed"
        
        try:
            ws = websocket.WebSocket()
            ws.settimeout(5)
            ws.connect("ws://localhost:8000/ws/health")
            
            # Send ping
            ws.send('{"type": "ping"}')
            
            # Try to receive
            try:
                response = ws.recv()
                ws.close()
                return True, f"WebSocket connected. Response: {response[:100]}"
            except:
                ws.close()
                return True, "WebSocket connected (no immediate response)"
        except websocket.WebSocketTimeoutException:
            return False, "WebSocket connection timed out"
        except Exception as e:
            return False, f"WebSocket error: {str(e)}"

    def check_dashboard_apis(self) -> Tuple[bool, str]:
        """Check dashboard API endpoints."""
        endpoints = [
            ("/api/health", "Dashboard health"),
            ("/api/dashboard/health", "Health score"),
            ("/api/categories", "Categories"),
            ("/api/alerts", "Alerts"),
            ("/api/predictions", "Predictions"),
            ("/api/correlations", "Correlations"),
        ]
        
        results = []
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    results.append(f"{name}: OK")
                else:
                    results.append(f"{name}: {response.status_code}")
            except Exception as e:
                results.append(f"{name}: Error")
        
        failures = [r for r in results if ": OK" not in r]
        if failures:
            return False, f"Failed endpoints: {', '.join(failures)}"
        
        return True, f"All {len(endpoints)} dashboard APIs working: {', '.join(results)}"

    def check_data_freshness(self) -> Tuple[bool, str]:
        """Check if data is fresh (not stale)."""
        try:
            # Check component last_seen timestamps
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="infrasense",
                password="infrasense",
                dbname="infrasense",
                connect_timeout=5
            )
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM components 
                WHERE last_seen > NOW() - INTERVAL '5 minutes'
            """)
            fresh_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM components")
            total_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            if total_count == 0:
                return False, "No components to check freshness"
            
            if fresh_count == 0:
                return False, f"All {total_count} components have stale data (>5 min old)"
            
            return True, f"{fresh_count}/{total_count} components have fresh data (<5 min old)"
        except Exception as e:
            return False, f"Error: {str(e)}"

    # =========================================================================
    # Main Run Method
    # =========================================================================
    
    def run_all_checks(self, skip_docker: bool = False) -> bool:
        """Run all verification checks."""
        print(f"\n{Colors.BOLD}{'='*60}")
        print("InfraSense End-to-End Verification")
        print(f"{'='*60}{Colors.RESET}\n")
        
        checks = [
            ("Docker Services", self.check_docker_services, "Required services running"),
            ("Backend Health", self.check_backend_health, "Backend responding"),
            ("Database Connection", self.check_database_connection, "PostgreSQL accessible"),
            ("Database Tables", self.check_database_tables, "Required tables exist"),
            ("Component Discovery", self.check_component_discovery, "Components discovered"),
            ("Infrastructure Summary", self.check_infrastructure_summary, "Summary API works"),
            ("Metrics Ingestion", self.check_metrics_ingestion, "Metrics in database"),
            ("Data Freshness", self.check_data_freshness, "Data is recent"),
            ("WebSocket", self.check_websocket, "WebSocket connected"),
            ("Dashboard APIs", self.check_dashboard_apis, "All APIs responding"),
        ]
        
        if skip_docker:
            checks = checks[1:]  # Skip Docker check
        
        passed = 0
        failed = 0
        
        for i, (name, check_func, expected) in enumerate(checks, 1):
            print(f"\n[{i}/{len(checks)}] {name}")
            print("-" * 40)
            
            if skip_docker and i == 1:
                self.log("Skipping Docker check (--skip-docker)", "WARN")
                self.results.append({
                    "name": name,
                    "success": True,
                    "message": "Skipped",
                    "expected": expected,
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue
            
            if self.check(name, check_func, expected):
                passed += 1
            else:
                failed += 1
        
        # Print summary
        print(f"\n{Colors.BOLD}{'='*60}")
        print("RESULTS SUMMARY")
        print(f"{'='*60}{Colors.RESET}\n")
        
        for result in self.results:
            status = f"{Colors.GREEN}✓{Colors.RESET}" if result["success"] else f"{Colors.RED}✗{Colors.RESET}"
            print(f"{status} {result['name']}")
            if not result["success"]:
                print(f"   {Colors.RED}→{Colors.RESET} {result['message']}")
        
        print(f"\n{Colors.BOLD}{'='*60}")
        if failed == 0:
            print(f"{Colors.GREEN}RESULT: PASS ({passed}/{len(checks)} checks){Colors.RESET}")
        else:
            print(f"{Colors.RED}RESULT: FAIL ({passed}/{len(checks)} passed, {failed} failed){Colors.RESET}")
        print(f"{'='*60}{Colors.RESET}\n")
        
        return failed == 0


def main():
    parser = argparse.ArgumentParser(description="InfraSense E2E Verification")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker checks")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()
    
    verifier = E2EVerifier(verbose=args.verbose)
    success = verifier.run_all_checks(skip_docker=args.skip_docker)
    
    if args.json:
        print(json.dumps(verifier.results, indent=2))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()