import os
import json
import pandas as pd
from typing import Dict, Any, List
from openai import OpenAI

class SimpleVEChatAgent:
    """Simplified VE Chat Agent for Lambda deployment."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        
        # Load data (this will be done once per Lambda cold start)
        self.data = self._load_data()
        
    def _load_data(self) -> Dict[str, Any]:
        """Load all data files."""
        data = {}
        
        try:
            # Load window counts
            data['window_counts'] = pd.read_csv('data/counts/count_windows.tsv', sep='\t')
            
            # Load door counts  
            data['door_counts'] = pd.read_csv('data/counts/count_unit_doors.tsv', sep='\t')
            
            # Load appliance counts
            data['appliance_counts'] = pd.read_csv('data/counts/count_appliance.tsv', sep='\t')
            
            # Load processed alternatives
            data['window_alternatives'] = pd.read_csv('data/processed/window_alternatives_scored.csv')
            data['door_alternatives'] = pd.read_csv('data/processed/door_alternatives_scored.csv')
            data['appliance_alternatives'] = pd.read_csv('data/processed/appliance_alternatives_scored.csv')
            
            # Load apartment specs
            data['apartment_specs'] = pd.read_csv('data/apartment_specs.csv')
            
            # Load total areas
            data['total_areas'] = pd.read_csv('data/total_areas.tsv', sep='\t')
            
        except Exception as e:
            print(f"Error loading data: {e}")
            # Return empty data structure
            data = {
                'window_counts': pd.DataFrame(),
                'door_counts': pd.DataFrame(), 
                'appliance_counts': pd.DataFrame(),
                'window_alternatives': pd.DataFrame(),
                'door_alternatives': pd.DataFrame(),
                'appliance_alternatives': pd.DataFrame(),
                'apartment_specs': pd.DataFrame(),
                'total_areas': pd.DataFrame()
            }
            
        return data
    
    def _get_data_summary(self) -> str:
        """Get a summary of all available data."""
        summary = []
        
        for name, df in self.data.items():
            if not df.empty:
                summary.append(f"- {name}: {len(df)} rows")
            else:
                summary.append(f"- {name}: No data available")
                
        return "\n".join(summary)
    
    def _get_window_counts_summary(self) -> str:
        """Get summary of window counts."""
        if self.data['window_counts'].empty:
            return "No window count data available."
            
        df = self.data['window_counts']
        total_windows = df.select_dtypes(include=['number']).sum().sum()
        
        summary = f"Total windows needed: {total_windows}\n\n"
        summary += "Window counts by mark and orientation:\n"
        
        for _, row in df.iterrows():
            mark = row['MARK']
            counts = []
            for col in df.columns[1:]:  # Skip MARK column
                if pd.notna(row[col]) and row[col] > 0:
                    counts.append(f"{col}: {int(row[col])}")
            
            if counts:
                summary += f"- {mark}: {', '.join(counts)}\n"
                
        return summary
    
    def _get_cost_summary(self) -> str:
        """Get cost summary from alternatives."""
        summary = []
        
        for material_type in ['window', 'door', 'appliance']:
            df = self.data[f'{material_type}_alternatives']
            if df.empty:
                continue
                
            # Get original costs (rank 0)
            originals = df[df['ALT_RANK'] == '0']
            if not originals.empty:
                total_original = originals['ORIGINAL_TOTAL_COST'].sum()
                summary.append(f"{material_type.title()}s - Original total cost: ${total_original:,.2f}")
                
        return "\n".join(summary) if summary else "No cost data available."
    
    def chat(self, message: str) -> str:
        """Process a chat message and return response."""
        
        # Create system prompt with data context
        system_prompt = f"""You are a Value Engineering AI assistant for building materials optimization. 

Available data:
{self._get_data_summary()}

You can answer questions about:
- Material counts and quantities (windows, doors, appliances)
- Cost analysis and savings
- Alternative material options
- Project specifications

Be helpful and provide specific information when available."""

        # Get relevant data based on the question
        data_context = ""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['window', 'windows']):
            data_context += f"\n\nWindow Data:\n{self._get_window_counts_summary()}"
            
        if any(word in message_lower for word in ['cost', 'price', 'saving', 'budget']):
            data_context += f"\n\nCost Data:\n{self._get_cost_summary()}"
        
        # Create the full prompt
        full_prompt = f"{system_prompt}{data_context}\n\nUser question: {message}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{data_context}\n\nUser question: {message}"}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error processing request: {str(e)}"

# Global instance for Lambda
agent = None

def get_agent():
    """Get or create the global agent instance."""
    global agent
    if agent is None:
        agent = SimpleVEChatAgent()
    return agent
