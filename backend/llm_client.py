import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Optional
import glob

# Load environment variables from .env file
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Optionally, add more providers here

def get_llm_client():
    """
    Get the appropriate LLM client based on the provider setting.
    This abstraction allows easy switching between different AI providers.
    """
    if LLM_PROVIDER == "openrouter":
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        return client
    elif LLM_PROVIDER == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        return client
    elif LLM_PROVIDER == "gemini":
        # Example: Gemini API integration placeholder
        # from gemini import GeminiClient
        # client = GeminiClient(api_key=GEMINI_API_KEY)
        # return client
        raise NotImplementedError("Gemini integration not implemented yet.")
    else:
        raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")

def load_policy_documents() -> Dict[str, str]:
    """
    Load all IT policy documents from the policies directory.
    This creates our knowledge base for the AI agent.
    
    Returns:
        Dictionary mapping policy names to their content
    """
    policies = {}
    policy_files = glob.glob("policies/*.txt")
    
    for file_path in policy_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Extract policy name from filename
                policy_name = os.path.basename(file_path).replace('.txt', '').replace('_', ' ').title()
                policies[policy_name] = file.read()
        except Exception as e:
            print(f"Error loading policy {file_path}: {e}")
    
    return policies

def search_policies(query: str, policies: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Smart policy search that includes context based on question type.
    
    Args:
        query: The search term or question
        policies: Dictionary of policy documents
    
    Returns:
        List of relevant policy sections
    """
    relevant_policies = []
    query_lower = query.lower()
    
    # Determine if this is likely a business/company question
    business_indicators = [
        'company', 'work', 'office', 'business', 'enterprise', 'corporate',
        'employee', 'staff', 'manager', 'supervisor', 'department',
        'policy', 'approval', 'permission', 'authorized', 'compliance'
    ]
    
    personal_indicators = [
        'my pc', 'my computer', 'my laptop', 'at home', 'personal',
        'my own', 'how to', 'how do i', 'can you help', 'install'
    ]
    
    is_business_context = any(indicator in query_lower for indicator in business_indicators)
    is_personal_context = any(indicator in query_lower for indicator in personal_indicators)
    
    # For clearly personal questions, provide minimal policy context
    if is_personal_context and not is_business_context:
        # Only include policy if it contains helpful technical guidance
        for policy_name, content in policies.items():
            if any(word in content.lower() for word in query_lower.split()):
                # Look for technical content, not just approval procedures
                paragraphs = content.split('\n\n')
                technical_paragraphs = []
                
                for paragraph in paragraphs:
                    # Include if it has technical steps, not just approval requirements
                    if (any(word in paragraph.lower() for word in query_lower.split()) and
                        any(tech_word in paragraph.lower() for tech_word in 
                            ['steps:', 'process:', 'install', 'configure', 'troubleshoot', 
                             'procedure', 'method', 'guide', 'how to'])):
                        technical_paragraphs.append(paragraph.strip())
                
                if technical_paragraphs:
                    relevant_policies.append({
                        'policy_name': f"{policy_name} (Technical Guide)",
                        'relevant_sections': technical_paragraphs[:2]  # Limit for personal questions
                    })
        return relevant_policies
    
    # For business questions or unclear context, include full policy context
    for policy_name, content in policies.items():
        if any(word in content.lower() for word in query_lower.split()):
            paragraphs = content.split('\n\n')
            relevant_paragraphs = []
            
            for paragraph in paragraphs:
                if any(word in paragraph.lower() for word in query_lower.split()):
                    relevant_paragraphs.append(paragraph.strip())
            
            if relevant_paragraphs:
                relevant_policies.append({
                    'policy_name': policy_name,
                    'relevant_sections': relevant_paragraphs[:3]  # Full context for business
                })
    
    return relevant_policies


class ITSupportAgent:
    """
    AI-powered IT Support Agent that provides policy-based guidance.
    
    This is the core of our chatbot - it:
    1. Understands user questions
    2. Searches relevant policies
    3. Provides step-by-step guidance
    4. Cites sources for transparency
    """
    
    def __init__(self):
        """Initialize the agent with LLM client and policy knowledge."""
        self.client = get_llm_client()
        self.policies = load_policy_documents()
        print(f"✅ IT Support Agent initialized with {len(self.policies)} policies")
    
    def get_ai_guidance(self, question: str, ticket_id: Optional[int] = None) -> Dict:
        """
        Get AI-powered guidance for an IT question.
        
        Args:
            question: The user's question or problem description
            ticket_id: Optional ticket ID for logging purposes
        
        Returns:
            Dictionary containing the agent's response, reasoning, and citations
        """
        try:
            # Step 1: Search for relevant policies
            relevant_policies = search_policies(question, self.policies)
            
            # Step 2: Prepare context for the AI
            policy_context = ""
            citations = []
            
            if relevant_policies:
                policy_context = "RELEVANT IT POLICIES:\n\n"
                for policy in relevant_policies:
                    policy_context += f"--- {policy['policy_name']} ---\n"
                    for section in policy['relevant_sections']:
                        policy_context += f"{section}\n\n"
                    citations.append(policy['policy_name'])
            
            # Step 3: Create system prompt for the AI
            system_prompt = """You are an expert IT Support Agent with extensive technical knowledge. Your primary mission is to provide helpful, practical technical assistance.

CORE PRINCIPLES:
1. Be HELPFUL first - provide detailed technical steps and solutions
2. Be COMPREHENSIVE - include troubleshooting, alternatives, and preventive measures  
3. Be PRACTICAL - focus on actionable guidance that users can follow
4. Be CONTEXT-AWARE - distinguish between personal and business IT scenarios
5. Be PROFESSIONAL but approachable and easy to understand

RESPONSE APPROACH:
- Lead with technical solutions and step-by-step instructions
- Provide multiple approaches when possible (beginner to advanced)
- Include troubleshooting for common issues
- Add relevant warnings or considerations naturally within the technical guidance
- Only mention approval requirements for clear business/security scenarios

OPTIMAL RESPONSE STRUCTURE:
TECHNICAL STEPS: [Detailed, numbered instructions with explanations]
TROUBLESHOOTING: [Common issues and solutions]
CONSIDERATIONS: [Important notes, requirements, alternatives]
ADDITIONAL HELP: [When to seek further assistance or escalate]

EXAMPLES OF GREAT RESPONSES:
- For "install Windows 10": Provide complete installation guide with system requirements, download links, step-by-step process, common issues, and post-installation setup
- For "password reset": Give self-service options first, then manual methods, then when to contact IT
- For "network issues": Start with basic troubleshooting steps, progress to advanced diagnostics, include command-line tools

Remember: Your goal is to solve problems and educate users. Be the helpful IT expert who provides comprehensive guidance while being mindful of security and best practices."""

            # Step 4: Get AI response
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"QUESTION: {question}\n\n{policy_context}"}
            ]
            
            # Choose model based on provider
            if LLM_PROVIDER == "openrouter":
                model = "meta-llama/llama-3.3-8b-instruct:free"
                extra_params = {
                    "extra_headers": {
                        "HTTP-Referer": "IT-Support-Agent",
                        "X-Title": "IT Support Agent",
                    },
                    "extra_body": {},
                }
            else:  # OpenAI
                model = "gpt-3.5-turbo"
                extra_params = {}
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more consistent responses
                **extra_params
            )
            
            ai_response = completion.choices[0].message.content
            
            # Step 5: Package the response
            result = {
                'success': True,
                'question': question,
                'ai_response': ai_response,
                'citations': citations,
                'policies_searched': len(relevant_policies),
                'ticket_id': ticket_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log the interaction if ticket_id provided
            if ticket_id:
                self._log_ai_interaction(ticket_id, result)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"AI guidance failed: {str(e)}",
                'question': question,
                'ticket_id': ticket_id
            }
    
    def _log_ai_interaction(self, ticket_id: int, interaction: Dict):
        """
        Log AI interaction to the ticket for transparency and auditing.
        
        Args:
            ticket_id: The ticket to log to
            interaction: The AI interaction details
        """
        try:
            import database as db
            log_entry = {
                'timestamp': interaction['timestamp'],
                'action': 'ai_guidance_provided',
                'question': interaction['question'],
                'ai_response': interaction['ai_response'],
                'citations': interaction['citations'],
                'policies_searched': interaction['policies_searched']
            }
            db.add_log_entry(ticket_id, log_entry)
        except Exception as e:
            print(f"Failed to log AI interaction: {e}")

# Global instance for easy access
_agent_instance = None

def get_agent() -> ITSupportAgent:
    """Get a singleton instance of the IT Support Agent."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ITSupportAgent()
    return _agent_instance

# Example usage and testing
if __name__ == "__main__":
    # Test the IT Support Agent
    agent = get_agent()
    
    # Test question
    test_question = "I forgot my password and can't log into my email. What should I do?"
    
    print(f"Question: {test_question}")
    print("-" * 50)
    
    response = agent.get_ai_guidance(test_question)
    
    if response['success']:
        print("AI Response:")
        print(response['ai_response'])
        print(f"\nPolicies Referenced: {response['citations']}")
        print(f"Policies Searched: {response['policies_searched']}")
    else:
        print(f"Error: {response['error']}")
