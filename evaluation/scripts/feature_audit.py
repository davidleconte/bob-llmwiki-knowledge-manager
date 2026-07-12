"""Feature audit comparing implementation against references."""
import pandas as pd
from pathlib import Path
from typing import Dict, List


class FeatureAuditor:
    """Audit features against LLM-Wiki, Karpathy, and Bob best practices."""
    
    def __init__(self):
        self.features = []
    
    def load_comparison_matrix(self, csv_path: str = "../feature_comparison.csv") -> pd.DataFrame:
        """Load feature comparison matrix."""
        try:
            return pd.read_csv(csv_path)
        except FileNotFoundError:
            # Create default matrix
            return self.create_default_matrix()
    
    def create_default_matrix(self) -> pd.DataFrame:
        """Create default feature comparison matrix."""
        features = [
            {
                'Feature': 'Knowledge_Storage',
                'LLM_Wiki': 'MCP_Server',
                'Karpathy': 'Context_Opt',
                'Bob_Practices': 'Native_Tools',
                'Our_Implementation': 'File_Based',
                'Status': 'Complete',
                'Notes': 'Simpler architecture, no server needed'
            },
            {
                'Feature': 'Search',
                'LLM_Wiki': 'Graph_Queries',
                'Karpathy': 'Semantic',
                'Bob_Practices': 'search_file_content',
                'Our_Implementation': 'Full_Text',
                'Status': 'Complete',
                'Notes': 'Native tool integration'
            },
            {
                'Feature': 'Memory',
                'LLM_Wiki': 'Persistent_Store',
                'Karpathy': 'Context_Window',
                'Bob_Practices': 'save_memory',
                'Our_Implementation': 'Native_Memory',
                'Status': 'Complete',
                'Notes': 'Bob native feature'
            },
            {
                'Feature': 'Cross_References',
                'LLM_Wiki': 'Graph_Links',
                'Karpathy': 'Token_Efficiency',
                'Bob_Practices': 'Manual_Links',
                'Our_Implementation': 'Bidirectional',
                'Status': 'Complete',
                'Notes': 'Template-driven'
            },
            {
                'Feature': 'Templates',
                'LLM_Wiki': 'None',
                'Karpathy': 'Prompt_Templates',
                'Bob_Practices': 'Reusable_Prompts',
                'Our_Implementation': '4_Doc_Types',
                'Status': 'Complete',
                'Notes': 'Structured approach'
            },
            {
                'Feature': 'Export',
                'LLM_Wiki': 'Multiple_Formats',
                'Karpathy': 'N/A',
                'Bob_Practices': 'N/A',
                'Our_Implementation': '4_Formats',
                'Status': 'Complete',
                'Notes': 'Added value'
            },
            {
                'Feature': 'Validation',
                'LLM_Wiki': 'None',
                'Karpathy': 'N/A',
                'Bob_Practices': 'N/A',
                'Our_Implementation': 'Automated',
                'Status': 'Complete',
                'Notes': 'Quality assurance'
            },
            {
                'Feature': 'Token_Optimization',
                'LLM_Wiki': 'N/A',
                'Karpathy': 'Core_Principle',
                'Bob_Practices': 'Core_Practice',
                'Our_Implementation': 'Partial',
                'Status': 'Partial',
                'Notes': 'Need documentation'
            },
            {
                'Feature': 'Context_Management',
                'LLM_Wiki': 'N/A',
                'Karpathy': 'Core_Principle',
                'Bob_Practices': 'Core_Practice',
                'Our_Implementation': 'Implemented',
                'Status': 'Complete',
                'Notes': 'File references, selective loading'
            },
            {
                'Feature': 'Batch_Operations',
                'LLM_Wiki': 'N/A',
                'Karpathy': 'Efficiency',
                'Bob_Practices': 'Recommended',
                'Our_Implementation': 'Partial',
                'Status': 'Partial',
                'Notes': 'Could be improved'
            }
        ]
        
        df = pd.DataFrame(features)
        df.to_csv('../feature_comparison.csv', index=False)
        return df
    
    def analyze_features(self, df: pd.DataFrame) -> Dict[str, any]:
        """Analyze feature implementation status."""
        status_counts = df['Status'].value_counts().to_dict()
        
        gaps = df[df['Status'] != 'Complete']
        
        return {
            'total_features': len(df),
            'complete': status_counts.get('Complete', 0),
            'partial': status_counts.get('Partial', 0),
            'missing': status_counts.get('Missing', 0),
            'completion_rate': (status_counts.get('Complete', 0) / len(df)) * 100,
            'gaps': gaps[['Feature', 'Status', 'Notes']].to_dict('records')
        }
    
    def generate_report(self, output_file: str = "../reports/feature_audit.md") -> None:
        """Generate feature audit report."""
        df = self.load_comparison_matrix()
        analysis = self.analyze_features(df)
        
        # Format table manually (no tabulate dependency)
        table_lines = ["| Feature | LLM-Wiki | Karpathy | Bob Practices | Our Implementation | Status | Notes |"]
        table_lines.append("|---------|----------|----------|---------------|-------------------|--------|-------|")
        for _, row in df.iterrows():
            table_lines.append(f"| {row['Feature']} | {row['LLM_Wiki']} | {row['Karpathy']} | {row['Bob_Practices']} | {row['Our_Implementation']} | {row['Status']} | {row['Notes']} |")
        table_str = "\n".join(table_lines)
        
        report = f"""# Feature Audit Report

## Summary
- **Total Features**: {analysis['total_features']}
- **Complete**: {analysis['complete']}
- **Partial**: {analysis['partial']}
- **Missing**: {analysis['missing']}
- **Completion Rate**: {analysis['completion_rate']:.1f}%

## Feature Comparison Matrix

{table_str}

## Gaps Identified

"""
        
        if analysis['gaps']:
            for gap in analysis['gaps']:
                report += f"### {gap['Feature']}\n"
                report += f"- **Status**: {gap['Status']}\n"
                report += f"- **Notes**: {gap['Notes']}\n\n"
        else:
            report += "✅ No gaps identified. All features complete.\n\n"
        
        report += """
## Recommendations

"""
        
        if analysis['completion_rate'] >= 90:
            report += "✅ **Excellent**: Feature implementation is comprehensive.\n"
        elif analysis['completion_rate'] >= 70:
            report += "⚠️ **Good**: Most features implemented, address remaining gaps.\n"
        else:
            report += "❌ **Needs Work**: Significant gaps in feature implementation.\n"
        
        report += "\n### Specific Actions\n\n"
        
        for gap in analysis['gaps']:
            report += f"- [ ] Complete {gap['Feature']}: {gap['Notes']}\n"
        
        report += "\n---\n*Generated by Feature Auditor*\n"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"✅ Generated feature audit report: {output_path}")


if __name__ == "__main__":
    auditor = FeatureAuditor()
    df = auditor.load_comparison_matrix()
    print(f"Loaded {len(df)} features")
    
    analysis = auditor.analyze_features(df)
    print(f"\nCompletion Rate: {analysis['completion_rate']:.1f}%")
    print(f"Gaps: {len(analysis['gaps'])}")
    
    auditor.generate_report()
