#!/usr/bin/env bash
# Quick script to check experiment status

cd /home/ubuntu/RPT-SSB-ASSESSMENT

echo "=== Experiment Status Check ==="
echo ""

# Check if process is running
PID=$(pgrep -f "run_all_scale_factors.sh" | head -1)
if [ -n "$PID" ]; then
    echo "✅ Process is RUNNING (PID: $PID)"
    echo "   CPU: $(ps -p $PID -o %cpu --no-headers 2>/dev/null || echo 'N/A')%"
    echo "   Memory: $(ps -p $PID -o %mem --no-headers 2>/dev/null || echo 'N/A')%"
else
    echo "❌ Process is NOT running"
fi

echo ""
echo "=== Results Files ==="
echo "SF=5:"
ls -1 results/sf5/*.csv 2>/dev/null | wc -l | xargs echo "  Files:"
echo "SF=10:"
ls -1 results/sf10/*.csv 2>/dev/null | wc -l | xargs echo "  Files:"

echo ""
echo "=== Recent Log Activity ==="
tail -5 experiment_run_background.log 2>/dev/null || echo "No log file yet"

echo ""
echo "=== Estimated Time Remaining ==="
if [ -n "$PID" ]; then
    if [ -f results/sf10/ssb_baseline.csv ]; then
        echo "✅ All experiments COMPLETE!"
    elif [ -f results/sf10/ssb_rpt.csv ]; then
        echo "⏳ SF=10 baseline in progress (~5-7 min remaining)"
    elif [ -f results/sf5/ssb_baseline.csv ]; then
        echo "⏳ SF=10 starting (~12-15 min remaining)"
    else
        echo "⏳ SF=5 in progress (~5-10 min remaining)"
    fi
else
    echo "Process completed or stopped"
fi

