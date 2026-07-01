import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── LOAD ──────────────────────────────────────────────────────────
df = pd.read_csv('insurance.csv')

# ── INSPECT ───────────────────────────────────────────────────────
print(f"Shape: {df.shape}")
print(f"\nColumn types:\n{df.dtypes}")
print(f"\nNull values:\n{df.isnull().sum()}")
print(f"\nDuplicate rows: {df.duplicated().sum()}")
print(f"\nFirst 5 rows:\n{df.head()}")
print(f"\nCharges stats:\n{df['charges'].describe().round(2)}")
print(f"\nSmoker split:\n{df['smoker'].value_counts()}")
print(f"\nRegion split:\n{df['region'].value_counts()}")

# ── REMOVE 1 DUPLICATE ROW ────────────────────────────────────────
df = df.drop_duplicates()

print(f"Rows after dedup: {len(df)}")   # Should show 1,337
print(f"Duplicates remaining: {df.duplicated().sum()}")  # Should show 0

# ── AGE GROUP (boundaries shifted to .5 — ages are integers, so this guarantees
#    an exact, unambiguous match with SQL's "BETWEEN 18 AND 24" style logic) ──
df['AgeGroup'] = pd.cut(df['age'],
    bins=[17.5, 24.5, 34.5, 44.5, 54.5, 64.5],
    labels=['18-24', '25-34', '35-44', '45-54', '55-64'])

# ── BMI GROUP (right=False makes each bin [a, b) — left-inclusive, right-exclusive —
#    matching SQL's "bmi < 18.5" / "BETWEEN 18.5 AND 24.99" style logic exactly) ──
df['BMIGroup'] = pd.cut(df['bmi'],
    bins=[0, 18.5, 25, 30, 35, 100],
    right=False,
    labels=['Underweight', 'Normal', 'Overweight', 'Obese', 'Severely Obese'])

# ── CHARGES BUCKET (same right=False logic) ───────────────────────
df['ChargesBucket'] = pd.cut(df['charges'],
    bins=[0, 5000, 10000, 20000, 35000, 100000],
    right=False,
    labels=['Under 5K', '5K-10K', '10K-20K', '20K-35K', '35K+'])

# ── RISK LEVEL (same right=False logic) ───────────────────────────
df['RiskLevel'] = pd.cut(df['charges'],
    bins=[0, 5000, 15000, 100000],
    right=False,
    labels=['Low Risk', 'Medium Risk', 'High Risk'])

# ── CHILDREN GROUP ────────────────────────────────────────────────
df['ChildrenGroup'] = df['children'].apply(
    lambda x: 'No Children' if x == 0 else ('1-2 Children' if x <= 2 else '3+ Children'))

# ── SMOKER BINARY ─────────────────────────────────────────────────
df['SmokerBin'] = (df['smoker'] == 'yes').astype(int)

print("Derived columns created ✅")
print(df[['AgeGroup','BMIGroup','ChargesBucket','RiskLevel','ChildrenGroup','SmokerBin']].head(4))

fig, ax = plt.subplots(figsize=(10, 5))

ax.hist(df['charges'], bins=50, color='#00B4D8', edgecolor='white',
        linewidth=0.4, alpha=0.8, density=True)

df['charges'].plot.kde(ax=ax, color='#E74C3C', linewidth=2.5)

ax.axvline(df['charges'].mean(),   color='#F39C12', linestyle='--', linewidth=2,
           label=f"Mean: ${df['charges'].mean():,.0f}")
ax.axvline(df['charges'].median(), color='#2ECC71', linestyle='--', linewidth=2,
           label=f"Median: ${df['charges'].median():,.0f}")

ax.set_xlabel('Insurance Charges ($)', fontsize=11)
ax.set_ylabel('Density', fontsize=11)
ax.set_title('Insurance Charges Distribution\nRight-skewed — Mean ($13,279) pulled above Median ($9,386) by high-cost smoker claims',
             fontsize=12, fontweight='bold')
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('chart1_charges_distribution.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 1 saved ✅")

fig, ax = plt.subplots(figsize=(9, 5))

groups = [df[df['smoker']=='no']['charges'],
          df[df['smoker']=='yes']['charges']]

bp = ax.boxplot(groups,
                labels=['Non-Smoker\n(n=1,063)', 'Smoker\n(n=274)'],
                patch_artist=True,
                medianprops=dict(color='white', linewidth=2.5))

bp['boxes'][0].set_facecolor('#2ECC71')
bp['boxes'][1].set_facecolor('#E74C3C')

no_med  = df[df['smoker']=='no']['charges'].median()
yes_med = df[df['smoker']=='yes']['charges'].median()
no_avg  = df[df['smoker']=='no']['charges'].mean()
yes_avg = df[df['smoker']=='yes']['charges'].mean()

ax.annotate(f'Median: ${no_med:,.0f}',  xy=(1, no_med),  xytext=(1.3, no_med + 1500),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9, fontweight='bold')
ax.annotate(f'Median: ${yes_med:,.0f}', xy=(2, yes_med), xytext=(1.55, yes_med + 2000),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9, fontweight='bold',
            color='#c0392b')

ax.set_ylabel('Annual Insurance Charges ($)', fontsize=11)
ax.set_title('Smoker vs Non-Smoker — Insurance Charges\nSmokers pay 3.80× MORE — the single dominant cost driver in the dataset',
             fontsize=12, fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

avg_patch_ns = mpatches.Patch(color='#2ECC71', label=f'Non-Smoker Avg: ${no_avg:,.0f}')
avg_patch_s  = mpatches.Patch(color='#E74C3C', label=f'Smoker Avg: ${yes_avg:,.0f}')
ax.legend(handles=[avg_patch_ns, avg_patch_s], fontsize=10)
plt.tight_layout()
plt.savefig('chart2_smoker_charges.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 2 saved ✅")

fig, ax = plt.subplots(figsize=(10, 5))

age_avg = df.groupby('AgeGroup', observed=True)['charges'].mean()
colors_a = ['#2ECC71','#F39C12','#E67E22','#E74C3C','#C0392B']

bars = ax.bar(age_avg.index, age_avg.values, color=colors_a, edgecolor='white')
for bar, val in zip(bars, age_avg.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 150,
            f'${val:,.0f}', ha='center', fontsize=10, fontweight='bold')

ax.axhline(df['charges'].mean(), color='navy', linestyle='--', linewidth=1.5,
           label=f'Overall Avg: ${df["charges"].mean():,.0f}')
ax.set_xlabel('Age Group', fontsize=11)
ax.set_ylabel('Average Insurance Charges ($)', fontsize=11)
ax.set_title('Average Insurance Charges by Age Group\nCosts double from youngest (18-24: $9,038) to oldest (55-64: $18,513)',
             fontsize=12, fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(fontsize=10)
ax.set_ylim(0, 22000)
plt.tight_layout()
plt.savefig('chart3_charges_by_age.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 3 saved ✅")

fig, ax = plt.subplots(figsize=(10, 6))

for smoker_val, color, label, alpha in [
    ('no',  '#2ECC71', 'Non-Smoker', 0.5),
    ('yes', '#E74C3C', 'Smoker',     0.7)
]:
    subset = df[df['smoker'] == smoker_val]
    ax.scatter(subset['bmi'], subset['charges'],
               color=color, alpha=alpha, s=25, label=label)

ax.axvline(x=30, color='orange', linestyle='--', linewidth=1.5, label='BMI 30 = Obese threshold')
ax.set_xlabel('BMI (Body Mass Index)', fontsize=11)
ax.set_ylabel('Insurance Charges ($)', fontsize=11)
ax.set_title('BMI vs Insurance Charges — Coloured by Smoker Status\nSmokers cluster in the high-charge zone | Obese Smokers = extreme cost territory',
             fontsize=12, fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig('chart4_bmi_charges_scatter.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 4 saved ✅")

fig, ax = plt.subplots(figsize=(9, 5))

reg_avg = df.groupby('region')['charges'].mean().sort_values(ascending=False)
colors_r = ['#E74C3C','#F39C12','#3498DB','#2ECC71']

bars = ax.bar(reg_avg.index, reg_avg.values, color=colors_r, edgecolor='white', width=0.5)
for bar, val in zip(bars, reg_avg.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
            f'${val:,.0f}', ha='center', fontsize=11, fontweight='bold')

ax.axhline(df['charges'].mean(), color='navy', linestyle='--', linewidth=1.5,
           label=f'Overall Avg: ${df["charges"].mean():,.0f}')
ax.set_ylabel('Average Insurance Charges ($)', fontsize=11)
ax.set_title('Average Insurance Charges by Region\nSoutheast leads at $14,735 | Southwest lowest at $12,347',
             fontsize=12, fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(fontsize=10)
ax.set_ylim(0, 18000)
plt.tight_layout()
plt.savefig('chart5_charges_by_region.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 5 saved ✅")

df['ChargesBucket'] = pd.cut(df['charges'],
    bins=[0, 5000, 10000, 20000, 35000, 100000],
    right=False,
    labels=['Under\n$5K', '$5K-\n$10K', '$10K-\n$20K', '$20K-\n$35K', 'Over\n$35K'])

bucket_data = df.groupby('ChargesBucket', observed=True).agg(
    count=('charges','count'),
    smoker_pct=('smoker', lambda x: round((x=='yes').sum()/len(x)*100,1))
).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 5))
colors_b = ['#2ECC71','#1ABC9C','#F39C12','#E67E22','#E74C3C']

bars = ax1.bar(bucket_data['ChargesBucket'], bucket_data['count'],
               color=colors_b, edgecolor='white')
for bar, cnt in zip(bars, bucket_data['count']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 4,
             str(cnt), ha='center', fontsize=10, fontweight='bold')

ax2 = ax1.twinx()
ax2.plot(bucket_data['ChargesBucket'], bucket_data['smoker_pct'],
         color='#9B59B6', marker='o', linewidth=2.5, markersize=8, label='Smoker %')
for i, (x, y) in enumerate(zip(bucket_data['ChargesBucket'], bucket_data['smoker_pct'])):
    ax2.annotate(f'{y}%', (x, y), textcoords='offset points',
                 xytext=(8, 4), fontsize=9, color='#9B59B6', fontweight='bold')

ax1.set_ylabel('Number of Patients', fontsize=11)
ax2.set_ylabel('Smoker % in Bucket', fontsize=11, color='#9B59B6')
ax1.set_xlabel('Charges Bucket', fontsize=11)
ax1.set_title('Claims Volume by Charge Bucket + Smoker % (Purple Line)\nOver \\$35K claims: 97.7% smokers | Under \\$10K claims: 0% smokers',
              fontsize=12, fontweight='bold')
ax2.set_ylim(0, 115)
ax2.tick_params(axis='y', labelcolor='#9B59B6')
ax2.legend(loc='upper left', fontsize=10)
plt.tight_layout()
plt.savefig('chart6_charges_bucket_smoker.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 6 saved ✅")

df['BMIGroup'] = pd.cut(df['bmi'],
    bins=[0, 18.5, 25, 30, 35, 100],
    right=False,
    labels=['Underweight', 'Normal', 'Overweight', 'Obese', 'Severely\nObese'])

bmi_smoke = df.groupby(['BMIGroup','smoker'], observed=True)['charges'].mean().unstack()

fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(bmi_smoke.index))
width = 0.35

bars1 = ax.bar(x - width/2, bmi_smoke['no'],  width, label='Non-Smoker', color='#2ECC71', edgecolor='white')
bars2 = ax.bar(x + width/2, bmi_smoke['yes'], width, label='Smoker',     color='#E74C3C', edgecolor='white')

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
            f'${bar.get_height():,.0f}', ha='center', fontsize=8, fontweight='bold')
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
            f'${bar.get_height():,.0f}', ha='center', fontsize=8,
            fontweight='bold', color='#c0392b')

ax.set_xticks(x)
ax.set_xticklabels(bmi_smoke.index, fontsize=10)
ax.set_ylabel('Average Insurance Charges ($)', fontsize=11)
ax.set_title('BMI Group vs Avg Charges — by Smoker Status\nObese Smokers: \\$39,641 | Non-Smoker Normal: \\$7,686 — a 5.16× gap within same BMI category',
             fontsize=12, fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(fontsize=11)
ax.set_ylim(0, 50000)
plt.tight_layout()
plt.savefig('chart7_bmi_smoker_charges.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 7 saved ✅")

df['RiskLevel'] = pd.cut(df['charges'],
    bins=[0, 5000, 15000, 100000],
    right=False,
    labels=['Low Risk\n(<$5K)', 'Medium Risk\n($5K-$15K)', 'High Risk\n(>$15K)'])

risk_profile = df.groupby('RiskLevel', observed=True).agg(
    count=('charges','count'),
    smoker_pct=('smoker', lambda x: (x=='yes').sum()/len(x)*100),
    avg_age=('age','mean'),
    avg_bmi=('bmi','mean'),
    avg_charges=('charges','mean')
).round(1)

fig, axes = plt.subplots(1, 3, figsize=(13, 5))
metrics = [('smoker_pct','Smoker %','#E74C3C'),
           ('avg_age','Average Age','#F39C12'),
           ('avg_bmi','Average BMI','#3498DB')]

for ax, (col, label, color) in zip(axes, metrics):
    bars = ax.bar(risk_profile.index, risk_profile[col],
                  color=[color]*3, edgecolor='white', alpha=0.85)
    for bar, val in zip(bars, risk_profile[col]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{val:.1f}', ha='center', fontsize=11, fontweight='bold')
    ax.set_title(label, fontsize=12, fontweight='bold')
    ax.set_ylabel(label, fontsize=10)
    ax.tick_params(axis='x', labelsize=9)

fig.suptitle('Risk Level Profile — Low / Medium / High Cost Patients\nHigh-Risk patients: 74.6% smokers · Avg age 40.2 · Avg BMI 31.1',
             fontsize=12, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('chart8_risk_level_profile.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 8 saved ✅")

fig, ax = plt.subplots(figsize=(10, 6))

for smoker_val, color, label, alpha in [
    ('no',  '#2ECC71', 'Non-Smoker', 0.5),
    ('yes', '#E74C3C', 'Smoker',     0.7)
]:
    subset = df[df['smoker'] == smoker_val]
    ax.scatter(subset['age'], subset['charges'],
               color=color, alpha=alpha, s=25, label=label)

ax.set_xlabel('Age (years)', fontsize=11)
ax.set_ylabel('Insurance Charges ($)', fontsize=11)
ax.set_title('Age vs Insurance Charges — Coloured by Smoker Status\nThree distinct cost bands visible — lower non-smoker band + two smoker tiers',
             fontsize=12, fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig('chart9_age_charges_scatter.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 9 saved ✅")

df_corr = df.copy()
df_corr['smoker_bin'] = (df_corr['smoker'] == 'yes').astype(int)
df_corr['sex_bin']    = (df_corr['sex'] == 'male').astype(int)

corr_matrix = df_corr[['age','bmi','children','smoker_bin','sex_bin','charges']].corr().round(3)
labels = ['Age','BMI','Children','Smoker','Sex (Male)','Charges']

fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='RdYlGn',
            center=0, vmin=-0.3, vmax=0.9,
            xticklabels=labels, yticklabels=labels,
            linewidths=0.5, linecolor='white', ax=ax,
            annot_kws={'size': 11, 'weight': 'bold'})
ax.set_title('Correlation Matrix — All Features vs Insurance Charges\nSmoker = 0.787 (dominant) | Age = 0.298 | BMI = 0.198 | Sex & Children = near-zero',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('chart10_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 10 saved ✅")

# ── DROP PYTHON-ONLY DERIVED COLUMNS BEFORE EXPORT ────────────────
df_export = df.drop(columns=['AgeGroup','BMIGroup','ChargesBucket',
                              'RiskLevel','ChildrenGroup','SmokerBin'])

df_export.to_csv('insurance_cleaned.csv', index=False, encoding='utf-8')

print(f"Exported: insurance_cleaned.csv")
print(f"Rows: {len(df_export)} | Columns: {df_export.shape[1]}")
print(f"Columns: {df_export.columns.tolist()}")