# scripts/generate_report.py
import json
from collections import Counter
from pathlib import Path

LOG_FILE = Path("logs/interactions.json")

def load_logs():
    if not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0:
        return []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def summarize_logs(logs):
    total_messages = len(logs)
    topics = Counter(entry.get("topic", "unknown") for entry in logs)
    escalations = sum(1 for entry in logs if entry.get("escalated"))
    mock_count = sum(1 for entry in logs if entry.get("mock_mode"))
    live_count = total_messages - mock_count

    # Extract hour from timestamp
    hours = [int(entry["timestamp"][11:13]) for entry in logs if "timestamp" in entry]
    busiest_hour = Counter(hours).most_common(1)[0][0] if hours else None

    most_common_topic = topics.most_common(1)[0][0] if topics else None

    # Client summary line
    resolved_count = total_messages - escalations
    summary_line = f"Sarah handled {total_messages} customer messages today. {resolved_count} were resolved instantly. {escalations} were escalated to you."

    return {
        "total_messages": total_messages,
        "topics_breakdown": dict(topics.most_common()),
        "total_escalations": escalations,
        "escalation_rate_percent": round((escalations / total_messages) * 100, 2) if total_messages else 0,
        "mock_mode_count": mock_count,
        "live_mode_count": live_count,
        "busiest_hour": busiest_hour,
        "most_common_topic": most_common_topic,
        "summary_line": summary_line
    }

def print_report(summary):
    if summary["total_messages"] == 0:
        print("No interactions recorded yet. Sarah is ready and waiting.")
        return

    print(f"Total messages handled: {summary['total_messages']}")
    print("Breakdown by topic (highest to lowest):")
    for topic, count in summary["topics_breakdown"].items():
        print(f"  {topic}: {count}")
    print(f"Total escalations: {summary['total_escalations']} ({summary['escalation_rate_percent']}%)")
    print(f"Mock mode interactions: {summary['mock_mode_count']}")
    print(f"Live OpenAI interactions: {summary['live_mode_count']}")
    print(f"Busiest hour of day: {summary['busiest_hour']}")
    print(f"Most common topic: {summary['most_common_topic']}")
    print(f"Client summary: {summary['summary_line']}")

if __name__ == "__main__":
    logs = load_logs()
    summary = summarize_logs(logs)
    print_report(summary)