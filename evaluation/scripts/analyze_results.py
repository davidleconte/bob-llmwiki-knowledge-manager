"""Statistical analysis for adversarial review results."""
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Tuple, Optional
import json


class ResultsAnalyzer:
    """Analyze adversarial review results."""
    
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.df: Optional[pd.DataFrame] = None
    
    def load_data(self) -> pd.DataFrame:
        """Load all task data into DataFrame."""
        tasks = []
        for filepath in self.data_dir.glob("*.json"):
            with open(filepath, 'r') as f:
                task = json.load(f)
                # Flatten nested metrics
                flat_task = {
                    'task_id': task['task_id'],
                    'scenario': task['scenario'],
                    'condition': task['condition'],
                    'participant': task['participant'],
                    'timestamp': task['timestamp'],
                    'tokens_used': task['metrics']['tokens_used'],
                    'bobcoin_cost': task['metrics']['bobcoin_cost'],
                    'time_seconds': task['metrics']['time_seconds'],
                    'quality_total': task['metrics']['quality_score']['total'],
                    'quality_completeness': task['metrics']['quality_score']['completeness'],
                    'quality_accuracy': task['metrics']['quality_score']['accuracy'],
                    'quality_consistency': task['metrics']['quality_score']['consistency'],
                    'quality_usability': task['metrics']['quality_score']['usability'],
                    'cross_references': task['metrics']['cross_references'],
                    'search_queries': task['metrics']['search_queries'],
                    'memory_recalls': task['metrics']['memory_recalls']
                }
                tasks.append(flat_task)
        
        self.df = pd.DataFrame(tasks)
        return self.df
    
    def calculate_token_savings(self) -> Dict[str, float]:
        """Calculate token savings statistics."""
        if self.df is None:
            self.load_data()
        
        control = self.df[self.df['condition'] == 'control']['tokens_used']
        treatment = self.df[self.df['condition'] == 'treatment']['tokens_used']
        
        if len(control) == 0 or len(treatment) == 0:
            return {'error': 'Insufficient data'}
        
        mean_control = control.mean()
        mean_treatment = treatment.mean()
        savings_pct = ((mean_control - mean_treatment) / mean_control) * 100
        
        return {
            'mean_control': mean_control,
            'mean_treatment': mean_treatment,
            'savings_tokens': mean_control - mean_treatment,
            'savings_percent': savings_pct,
            'std_control': control.std(),
            'std_treatment': treatment.std()
        }
    
    def statistical_test(self) -> Dict[str, float]:
        """Perform paired t-test for token usage."""
        if self.df is None:
            self.load_data()
        
        # Group by participant and scenario for pairing
        control = self.df[self.df['condition'] == 'control'].sort_values(['participant', 'scenario'])
        treatment = self.df[self.df['condition'] == 'treatment'].sort_values(['participant', 'scenario'])
        
        if len(control) != len(treatment):
            # Use independent samples t-test if pairing not possible
            t_stat, p_value = stats.ttest_ind(
                control['tokens_used'],
                treatment['tokens_used']
            )
            test_type = 'independent'
        else:
            # Use paired t-test
            t_stat, p_value = stats.ttest_rel(
                control['tokens_used'],
                treatment['tokens_used']
            )
            test_type = 'paired'
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt((control['tokens_used'].std()**2 + treatment['tokens_used'].std()**2) / 2)
        cohens_d = (control['tokens_used'].mean() - treatment['tokens_used'].mean()) / pooled_std
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'test_type': test_type,
            'cohens_d': cohens_d,
            'effect_size': 'small' if abs(cohens_d) < 0.5 else 'medium' if abs(cohens_d) < 0.8 else 'large'
        }
    
    def quality_analysis(self) -> Dict[str, float]:
        """Analyze quality scores."""
        if self.df is None:
            self.load_data()
        
        control = self.df[self.df['condition'] == 'control']['quality_total']
        treatment = self.df[self.df['condition'] == 'treatment']['quality_total']
        
        if len(control) == 0 or len(treatment) == 0:
            return {'error': 'Insufficient data'}
        
        # Test if quality is maintained or improved
        t_stat, p_value = stats.ttest_ind(treatment, control)
        
        return {
            'mean_control': control.mean(),
            'mean_treatment': treatment.mean(),
            'difference': treatment.mean() - control.mean(),
            'improvement_percent': ((treatment.mean() - control.mean()) / control.mean()) * 100,
            't_statistic': t_stat,
            'p_value': p_value,
            'quality_maintained': treatment.mean() >= control.mean()
        }
    
    def cost_benefit_analysis(self) -> Dict[str, float]:
        """Calculate cost-benefit metrics."""
        if self.df is None:
            self.load_data()
        
        control = self.df[self.df['condition'] == 'control']
        treatment = self.df[self.df['condition'] == 'treatment']
        
        total_savings = control['bobcoin_cost'].sum() - treatment['bobcoin_cost'].sum()
        avg_savings_per_task = total_savings / len(treatment) if len(treatment) > 0 else 0
        
        # Assume 5 minutes setup time
        setup_cost_seconds = 5 * 60
        avg_time_savings = control['time_seconds'].mean() - treatment['time_seconds'].mean()
        break_even_tasks = setup_cost_seconds / avg_time_savings if avg_time_savings > 0 else float('inf')
        
        return {
            'total_bobcoin_savings': total_savings,
            'avg_savings_per_task': avg_savings_per_task,
            'avg_time_savings_seconds': avg_time_savings,
            'break_even_tasks': break_even_tasks,
            'roi_percent': (total_savings / 0.01) * 100 if total_savings > 0 else 0  # Assume $0.01 setup cost
        }
    
    def plot_results(self, output_dir: str = "../results") -> None:
        """Create visualization of results."""
        if self.df is None:
            self.load_data()
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Token usage comparison
        sns.boxplot(data=self.df, x='condition', y='tokens_used', ax=axes[0, 0])
        axes[0, 0].set_title('Token Usage by Condition', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Condition')
        axes[0, 0].set_ylabel('Tokens Used')
        
        # 2. Quality scores
        sns.boxplot(data=self.df, x='condition', y='quality_total', ax=axes[0, 1])
        axes[0, 1].set_title('Quality Scores by Condition', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Condition')
        axes[0, 1].set_ylabel('Quality Score (0-100)')
        
        # 3. Time comparison
        sns.boxplot(data=self.df, x='condition', y='time_seconds', ax=axes[1, 0])
        axes[1, 0].set_title('Time by Condition', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Condition')
        axes[1, 0].set_ylabel('Time (seconds)')
        
        # 4. Cost comparison
        sns.boxplot(data=self.df, x='condition', y='bobcoin_cost', ax=axes[1, 1])
        axes[1, 1].set_title('Bobcoin Cost by Condition', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Condition')
        axes[1, 1].set_ylabel('Cost ($)')
        
        plt.tight_layout()
        plt.savefig(output_path / 'comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Saved visualization to {output_path / 'comparison.png'}")
    
    def generate_report(self, output_file: str = "../reports/analysis_report.md") -> None:
        """Generate comprehensive analysis report."""
        if self.df is None:
            self.load_data()
        
        token_savings = self.calculate_token_savings()
        stat_test = self.statistical_test()
        quality = self.quality_analysis()
        cost_benefit = self.cost_benefit_analysis()
        
        report = f"""# Adversarial Review Analysis Report

## Data Summary
- Total Tasks: {len(self.df)}
- Control Tasks: {len(self.df[self.df['condition'] == 'control'])}
- Treatment Tasks: {len(self.df[self.df['condition'] == 'treatment'])}
- Scenarios: {', '.join(self.df['scenario'].unique())}

## Token Efficiency Results

### Token Savings
- Mean Control: {token_savings.get('mean_control', 0):.0f} tokens
- Mean Treatment: {token_savings.get('mean_treatment', 0):.0f} tokens
- Savings: {token_savings.get('savings_tokens', 0):.0f} tokens ({token_savings.get('savings_percent', 0):.1f}%)

### Statistical Significance
- Test Type: {stat_test['test_type']}
- t-statistic: {stat_test['t_statistic']:.3f}
- p-value: {stat_test['p_value']:.4f}
- Significant: {'✅ Yes' if stat_test['significant'] else '❌ No'}
- Effect Size: {stat_test['effect_size']} (Cohen's d = {stat_test['cohens_d']:.3f})

## Quality Assessment

### Quality Scores
- Mean Control: {quality.get('mean_control', 0):.1f}/100
- Mean Treatment: {quality.get('mean_treatment', 0):.1f}/100
- Difference: {quality.get('difference', 0):+.1f} points ({quality.get('improvement_percent', 0):+.1f}%)
- Quality Maintained: {'✅ Yes' if quality.get('quality_maintained', False) else '❌ No'}

## Cost-Benefit Analysis

### Bobcoin Savings
- Total Savings: ${cost_benefit['total_bobcoin_savings']:.2f}
- Average per Task: ${cost_benefit['avg_savings_per_task']:.3f}
- ROI: {cost_benefit['roi_percent']:.0f}%

### Time Efficiency
- Average Time Savings: {cost_benefit['avg_time_savings_seconds']:.0f} seconds per task
- Break-even Point: {cost_benefit['break_even_tasks']:.0f} tasks

## Conclusions

{'✅ **SUCCESS**: Token savings target met (≥30%)' if token_savings.get('savings_percent', 0) >= 30 else '❌ **BELOW TARGET**: Token savings below 30%'}

{'✅ **SUCCESS**: Quality maintained or improved' if quality.get('quality_maintained', False) else '❌ **CONCERN**: Quality degradation detected'}

{'✅ **SIGNIFICANT**: Results are statistically significant (p < 0.05)' if stat_test['significant'] else '⚠️ **NOT SIGNIFICANT**: Results not statistically significant'}

## Recommendations

Based on the analysis:
1. {'Continue with current implementation' if token_savings.get('savings_percent', 0) >= 30 else 'Investigate token optimization opportunities'}
2. {'Quality standards are maintained' if quality.get('quality_maintained', False) else 'Review quality assurance processes'}
3. {'ROI is positive after {:.0f} tasks'.format(cost_benefit['break_even_tasks']) if cost_benefit['break_even_tasks'] < 100 else 'Consider optimizing setup time'}

---
*Generated: {pd.Timestamp.now().isoformat()}*
"""
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"✅ Generated report: {output_path}")


if __name__ == "__main__":
    # Example usage
    analyzer = ResultsAnalyzer()
    
    try:
        df = analyzer.load_data()
        print(f"Loaded {len(df)} tasks")
        
        if len(df) > 0:
            # Calculate metrics
            token_savings = analyzer.calculate_token_savings()
            print(f"\nToken Savings: {token_savings.get('savings_percent', 0):.1f}%")
            
            # Statistical test
            test_results = analyzer.statistical_test()
            print(f"P-value: {test_results['p_value']:.4f}")
            print(f"Significant: {test_results['significant']}")
            
            # Generate visualizations
            analyzer.plot_results()
            
            # Generate report
            analyzer.generate_report()
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Need more data to perform full analysis")
