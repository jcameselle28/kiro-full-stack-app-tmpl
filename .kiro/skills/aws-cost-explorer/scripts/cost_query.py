#!/usr/bin/env python3
"""
AWS Cost Explorer Query Script
Supports querying costs at service level and drilling down to usage type level.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Optional


def get_date_range(days_ago: int) -> tuple[str, str]:
    """Calculate date range."""
    target_date = datetime.now() - timedelta(days=days_ago)
    start_date = target_date.strftime("%Y-%m-%d")
    end_date = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")
    return start_date, end_date


def run_aws_command(cmd: list[str]) -> dict:
    """Execute AWS CLI command and return parsed JSON result."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"AWS CLI error: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)


def query_by_service(start_date: str, end_date: str, min_cost: float = 0) -> list[dict]:
    """Query costs grouped by service."""
    cmd = [
        "aws", "ce", "get-cost-and-usage",
        "--time-period", f"Start={start_date},End={end_date}",
        "--granularity", "DAILY",
        "--metrics", "UnblendedCost",
        "--group-by", "Type=DIMENSION,Key=SERVICE",
        "--output", "json"
    ]

    data = run_aws_command(cmd)
    results = []

    for group in data.get("ResultsByTime", [{}])[0].get("Groups", []):
        service = group["Keys"][0]
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if amount >= min_cost:
            results.append({
                "service": service,
                "amount": amount
            })

    return sorted(results, key=lambda x: x["amount"], reverse=True)


def query_by_usage_type(start_date: str, end_date: str, service: str, min_cost: float = 0) -> list[dict]:
    """Query cost breakdown by usage type for a specific service."""
    filter_expr = json.dumps({
        "Dimensions": {
            "Key": "SERVICE",
            "Values": [service]
        }
    })

    cmd = [
        "aws", "ce", "get-cost-and-usage",
        "--time-period", f"Start={start_date},End={end_date}",
        "--granularity", "DAILY",
        "--metrics", "UnblendedCost",
        "--filter", filter_expr,
        "--group-by", "Type=DIMENSION,Key=USAGE_TYPE",
        "--output", "json"
    ]

    data = run_aws_command(cmd)
    results = []

    for group in data.get("ResultsByTime", [{}])[0].get("Groups", []):
        usage_type = group["Keys"][0]
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if amount >= min_cost:
            results.append({
                "usage_type": usage_type,
                "amount": amount
            })

    return sorted(results, key=lambda x: x["amount"], reverse=True)


def query_all_usage_types(start_date: str, end_date: str, min_cost: float = 0) -> list[dict]:
    """Query usage type breakdown for all services."""
    cmd = [
        "aws", "ce", "get-cost-and-usage",
        "--time-period", f"Start={start_date},End={end_date}",
        "--granularity", "DAILY",
        "--metrics", "UnblendedCost",
        "--group-by", "Type=DIMENSION,Key=SERVICE", "Type=DIMENSION,Key=USAGE_TYPE",
        "--output", "json"
    ]

    data = run_aws_command(cmd)
    results = []

    for group in data.get("ResultsByTime", [{}])[0].get("Groups", []):
        service = group["Keys"][0]
        usage_type = group["Keys"][1]
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if amount >= min_cost:
            results.append({
                "service": service,
                "usage_type": usage_type,
                "amount": amount
            })

    return sorted(results, key=lambda x: x["amount"], reverse=True)


def format_currency(amount: float) -> str:
    """Format currency for display."""
    return f"${amount:.2f}"


def print_service_report(results: list[dict], date: str):
    """Print service-level report."""
    total = sum(r["amount"] for r in results)

    print(f"\n{'='*70}")
    print(f"📊 AWS Cost Report - {date} (by Service)")
    print(f"{'='*70}")
    print(f"{'Rank':<6}{'Service':<50}{'Cost (USD)':>12}")
    print(f"{'-'*70}")

    for i, r in enumerate(results, 1):
        print(f"{i:<6}{r['service']:<50}{format_currency(r['amount']):>12}")

    print(f"{'-'*70}")
    print(f"{'Total':<56}{format_currency(total):>12}")
    print()


def print_usage_type_report(results: list[dict], date: str, service: Optional[str] = None):
    """Print usage type level report."""
    total = sum(r["amount"] for r in results)

    title = f"by Usage Type - {service}" if service else "by Usage Type (all services)"

    print(f"\n{'='*90}")
    print(f"📊 AWS Cost Report - {date} ({title})")
    print(f"{'='*90}")

    if service:
        print(f"{'Rank':<6}{'Usage Type':<60}{'Cost (USD)':>12}")
        print(f"{'-'*90}")
        for i, r in enumerate(results, 1):
            print(f"{i:<6}{r['usage_type']:<60}{format_currency(r['amount']):>12}")
    else:
        print(f"{'Rank':<6}{'Service':<35}{'Usage Type':<35}{'Cost (USD)':>12}")
        print(f"{'-'*90}")
        for i, r in enumerate(results, 1):
            svc = r['service'][:33] + '..' if len(r['service']) > 35 else r['service']
            ut = r['usage_type'][:33] + '..' if len(r['usage_type']) > 35 else r['usage_type']
            print(f"{i:<6}{svc:<35}{ut:<35}{format_currency(r['amount']):>12}")

    print(f"{'-'*90}")
    print(f"{'Total':<76}{format_currency(total):>12}")
    print()


def output_json(results: list[dict], date: str):
    """Output in JSON format."""
    output = {
        "date": date,
        "items": results,
        "total": sum(r["amount"] for r in results)
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="AWS Cost Explorer Query Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query costs from 2 days ago (default) by service
  python cost_query.py

  # Query yesterday's costs, show items > $5
  python cost_query.py --days-ago 1 --min-cost 5

  # Query specific date
  python cost_query.py --date 2026-01-15

  # Query specific service's usage breakdown
  python cost_query.py --service "Amazon OpenSearch Service" --min-cost 1

  # Query all services with usage type details
  python cost_query.py --detailed --min-cost 5

  # Output as JSON
  python cost_query.py --json --min-cost 5
        """
    )

    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        "--days-ago", "-d",
        type=int,
        default=2,
        help="Query costs from N days ago (default: 2, i.e., day before yesterday)"
    )
    date_group.add_argument(
        "--date",
        type=str,
        help="Query costs for a specific date (format: YYYY-MM-DD)"
    )

    parser.add_argument(
        "--min-cost", "-m",
        type=float,
        default=0,
        help="Minimum cost threshold, only show items above this value (default: 0)"
    )

    parser.add_argument(
        "--service", "-s",
        type=str,
        help="Query usage type breakdown for a specific service"
    )

    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show all services with usage type breakdown"
    )

    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    # Determine date range
    if args.date:
        try:
            target = datetime.strptime(args.date, "%Y-%m-%d")
            start_date = args.date
            end_date = (target + timedelta(days=1)).strftime("%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format '{args.date}', please use YYYY-MM-DD format", file=sys.stderr)
            sys.exit(1)
    else:
        start_date, end_date = get_date_range(args.days_ago)

    # Execute query
    if args.service:
        results = query_by_usage_type(start_date, end_date, args.service, args.min_cost)
        if args.json:
            output_json(results, start_date)
        else:
            print_usage_type_report(results, start_date, args.service)
    elif args.detailed:
        results = query_all_usage_types(start_date, end_date, args.min_cost)
        if args.json:
            output_json(results, start_date)
        else:
            print_usage_type_report(results, start_date)
    else:
        results = query_by_service(start_date, end_date, args.min_cost)
        if args.json:
            output_json(results, start_date)
        else:
            print_service_report(results, start_date)


if __name__ == "__main__":
    main()
