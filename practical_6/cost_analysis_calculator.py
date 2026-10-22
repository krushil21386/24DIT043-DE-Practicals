import json
import os
import matplotlib.pyplot as plt

# Tier Pricing Rates ($ per GB per month)
PRICING = {
    "Hot": 0.0230,    # High Throughput NVMe/SSD
    "Warm": 0.0125,   # Infrequent Access HDD
    "Cold": 0.00099,  # Deep Compression Archiving
    "EXPIRED (DELETED)": 0.0000
}

def analyze_cost_reductions(manifest_before="outputs/dataset_manifest.json", manifest_after="outputs/updated_dataset_manifest.json"):
    os.makedirs("outputs", exist_ok=True)

    if not os.path.exists(manifest_after):
        from lifecycle_automation import evaluate_and_enforce_lifecycle
        evaluate_and_enforce_lifecycle()

    with open(manifest_before, "r") as f:
        before_objects = json.load(f)

    with open(manifest_after, "r") as f:
        after_objects = json.load(f)

    # 1. Baseline Cost (All data retained in HOT tier)
    total_gb = sum(obj["size_gb"] for obj in before_objects)
    baseline_monthly_cost = total_gb * PRICING["Hot"]
    baseline_annual_cost = baseline_monthly_cost * 12

    # 2. Optimized Tiered Cost
    optimized_monthly_cost = 0.0
    tier_gb_breakdown = {"Hot": 0.0, "Warm": 0.0, "Cold": 0.0, "EXPIRED (DELETED)": 0.0}

    for obj in after_objects:
        tier = obj["current_tier"]
        size = obj["size_gb"]
        tier_gb_breakdown[tier] += size
        optimized_monthly_cost += size * PRICING.get(tier, 0.0)

    optimized_annual_cost = optimized_monthly_cost * 12

    monthly_savings = baseline_monthly_cost - optimized_monthly_cost
    annual_savings = baseline_annual_cost - optimized_annual_cost
    pct_reduction = (monthly_savings / baseline_monthly_cost) * 100

    print("=" * 80)
    print("         FINANCIAL COST REDUCTION & STORAGE OPTIMIZATION REPORT          ")
    print("=" * 80)
    print(f" Total Dataset Capacity Evaluated: {total_gb:,.1f} GB ({total_gb/1024:.2f} TB)\n")
    print(" [1] BASELINE STORAGE COSTS (Unmanaged / All Hot Tier):")
    print(f"     - Monthly Baseline Cost:  ${baseline_monthly_cost:,.2f}")
    print(f"     - Annual Baseline Cost:   ${baseline_annual_cost:,.2f}\n")
    print(" [2] OPTIMIZED TIERED STORAGE COSTS (Automated ILM Matrix):")
    print(f"     - Hot Tier Storage ({tier_gb_breakdown['Hot']:,.1f} GB @ $0.023/GB):       ${tier_gb_breakdown['Hot']*PRICING['Hot']:,.2f}")
    print(f"     - Warm Tier Storage ({tier_gb_breakdown['Warm']:,.1f} GB @ $0.0125/GB):    ${tier_gb_breakdown['Warm']*PRICING['Warm']:,.2f}")
    print(f"     - Cold Tier Storage ({tier_gb_breakdown['Cold']:,.1f} GB @ $0.00099/GB):   ${tier_gb_breakdown['Cold']*PRICING['Cold']:,.2f}")
    print(f"     - Expired Data Purged ({tier_gb_breakdown['EXPIRED (DELETED)']:,.1f} GB @ $0.00):      $0.00")
    print(f"     - Total Monthly Optimized Cost: ${optimized_monthly_cost:,.2f}")
    print(f"     - Total Annual Optimized Cost:  ${optimized_annual_cost:,.2f}\n")
    print(" [3] SAVINGS SUMMARY:")
    print(f"     - Monthly Cost Reduction: ${monthly_savings:,.2f} ({pct_reduction:.2f}% savings)")
    print(f"     - Annual Cost Reduction:  ${annual_savings:,.2f} / year saved!\n")
    print("=" * 80)

    # Plot Cost Reduction Chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Bar chart: Baseline vs Optimized
    categories = ['Unmanaged Baseline (Hot Only)', 'Automated Tiered Lifecycle']
    costs = [baseline_monthly_cost, optimized_monthly_cost]
    colors = ['#e74c3c', '#2ecc71']

    bars = ax1.bar(categories, costs, color=colors, width=0.5)
    ax1.set_ylabel('Monthly Cost ($ USD)', fontsize=12, fontweight='bold')
    ax1.set_title('Monthly Operational Storage Cost Comparison', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"${yval:,.2f}", ha='center', va='bottom', fontweight='bold', fontsize=11)

    # Pie Chart: Storage Capacity Distribution by Tier
    tier_names = [k for k, v in tier_gb_breakdown.items() if v > 0]
    tier_sizes = [v for k, v in tier_gb_breakdown.items() if v > 0]
    pie_colors = ['#ff7675', '#ffeaa7', '#74b9ff', '#b2bec3']

    ax2.pie(tier_sizes, labels=tier_names, autopct='%1.1f%%', startangle=140, colors=pie_colors, textprops={'fontweight': 'bold'})
    ax2.set_title(f'Post-Policy Capacity Distribution (Total: {total_gb:,.0f} GB)', fontsize=13, fontweight='bold')

    plt.tight_layout()
    chart_path = "outputs/cost_reduction_chart.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()

    print(f"[+] Cost reduction breakdown graph generated and saved to: {chart_path}")

    # Generate Markdown Summary Report
    report_md = f"""# Practical 6: Automated Storage Lifecycle Policy - Financial Cost Reduction Breakdown

## Executive Cost Reduction Summary
- **Evaluated Data Capacity**: {total_gb:,.1f} GB ({total_gb/1024:.2f} TB)
- **Baseline Monthly Cost (All Hot)**: ${baseline_monthly_cost:,.2f}
- **Optimized Monthly Cost (Tiered ILM)**: ${optimized_monthly_cost:,.2f}
- **Monthly Net Savings**: **${monthly_savings:,.2f}** ({pct_reduction:.2f}% Cost Reduction)
- **Annualized Net Savings**: **${annual_savings:,.2f} / year**

## Capacity Breakdown by Storage Class
| Access Tier | Capacity (GB) | Percentage (%) | Unit Cost ($/GB/mo) | Monthly Cost ($) |
|---|---|---|---|---|
| **Hot (NVMe / SSD)** | {tier_gb_breakdown['Hot']:,.1f} GB | {(tier_gb_breakdown['Hot']/total_gb)*100:.1f}% | $0.0230 | ${tier_gb_breakdown['Hot']*PRICING['Hot']:,.2f} |
| **Warm (Infrequent Access)** | {tier_gb_breakdown['Warm']:,.1f} GB | {(tier_gb_breakdown['Warm']/total_gb)*100:.1f}% | $0.0125 | ${tier_gb_breakdown['Warm']*PRICING['Warm']:,.2f} |
| **Cold (Deep Archive)** | {tier_gb_breakdown['Cold']:,.1f} GB | {(tier_gb_breakdown['Cold']/total_gb)*100:.1f}% | $0.00099 | ${tier_gb_breakdown['Cold']*PRICING['Cold']:,.2f} |
| **Purged (Expired Temp Data)** | {tier_gb_breakdown['EXPIRED (DELETED)']:,.1f} GB | {(tier_gb_breakdown['EXPIRED (DELETED)']/total_gb)*100:.1f}% | $0.0000 | $0.00 |
| **TOTAL** | **{total_gb:,.1f} GB** | **100.0%** | -- | **${optimized_monthly_cost:,.2f}** |
"""
    with open("outputs/cost_reduction_report.md", "w") as f:
        f.write(report_md)

    return baseline_monthly_cost, optimized_monthly_cost, monthly_savings, pct_reduction

if __name__ == "__main__":
    analyze_cost_reductions()
