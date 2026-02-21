#!/usr/bin/env python3
"""
Gemini AI Agriculture Assistant
Advanced AI-powered chatbot using Google's Gemini API for intelligent responses
"""

import google.generativeai as genai
import json
import random
from datetime import datetime
from schemes_database import schemes_database, intent_keywords, detect_intent, get_schemes_by_intent, get_all_schemes
from translations import translations

class GeminiAgricultureBot:
    def __init__(self, language='en'):
        self.language = language
        self.t = translations[language]
        
        # Gemini API Keys - Using both for load balancing and fallback
        self.gemini_api_keys = [
            "AIzaSyDg5T18bwuIzk8n-YDgfhqyEkVup88iZtY",
            "AIzaSyDUJepqmkCUrK0fZXJ62gNA6iwpCRadzc8"
        ]
        self.current_key_index = 0
        
        # Initialize Gemini with the first API key
        try:
            genai.configure(api_key=self.gemini_api_keys[0])
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            self.api_working = True
        except Exception as e:
            print(f"Gemini API initialization failed: {e}")
            self.api_working = False
        
    def _switch_api_key(self):
        """Switch to the next API key if current one fails"""
        self.current_key_index = (self.current_key_index + 1) % len(self.gemini_api_keys)
        try:
            genai.configure(api_key=self.gemini_api_keys[self.current_key_index])
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            self.api_working = True
            return True
        except Exception as e:
            print(f"API key {self.current_key_index} failed: {e}")
            self.api_working = False
            return False
    
    def get_response(self, message, farmer_profile=None):
        """Generate intelligent response using Gemini AI"""
        try:
            # Detect intent first
            intent = detect_intent(message)
            
            # Get relevant schemes
            if intent != "general":
                relevant_schemes = get_schemes_by_intent(intent)
            else:
                relevant_schemes = get_all_schemes()
            
            # Filter schemes based on farmer profile if available
            if farmer_profile:
                relevant_schemes = self._filter_by_profile(relevant_schemes, farmer_profile)
            
            # Generate response using Gemini if API is working
            if self.api_working:
                gemini_response = self._get_gemini_response(message, intent, relevant_schemes, farmer_profile)
                if gemini_response:
                    return gemini_response
            
            # Fallback to enhanced rule-based response
            return self._get_fallback_response(message, intent, relevant_schemes, farmer_profile)
            
        except Exception as e:
            print(f"Error generating response: {e}")
            # Try switching API key and retry once
            if self._switch_api_key():
                return self.get_response(message, farmer_profile)
            else:
                return self._get_fallback_response(message, intent, relevant_schemes, farmer_profile)
    
    def _get_gemini_response(self, message, intent, schemes, profile):
        """Generate response using Gemini AI"""
        try:
            # Create context-aware prompt
            prompt = self._create_gemini_prompt(message, intent, schemes, profile)
            
            # Generate response with Gemini
            response = self.gemini_model.generate_content(prompt)
            
            if response.text:
                return self._format_gemini_response(response.text, intent, schemes)
            else:
                return None
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    def _create_gemini_prompt(self, message, intent, schemes, profile):
        """Create a comprehensive prompt for Gemini"""
        prompt = f"""
You are an expert agricultural assistant named AgriSahayak AI, helping Indian farmers with government schemes and farming advice.

USER QUERY: {message}
DETECTED INTENT: {intent}
USER PROFILE: {json.dumps(profile, indent=2) if profile else 'No profile available'}

AVAILABLE SCHEMES:
{json.dumps(schemes[:5], indent=2)}

INSTRUCTIONS:
1. Provide a warm, empathetic response in {self.language} language
2. Recommend the most relevant 2-3 schemes from the list above
3. Include practical farming advice related to their query
4. Add weather or market information if relevant
5. Use emojis to make the response engaging
6. Keep the response concise but comprehensive
7. End with a helpful follow-up question

Format your response with clear headings and bullet points for readability.
"""
        return prompt
    
    def _format_gemini_response(self, gemini_text, intent, schemes):
        """Format Gemini response to include scheme details"""
        # Add scheme details section
        scheme_details = "\n\n🎯 **Recommended Government Schemes**\n\n"
        
        for i, scheme in enumerate(schemes[:3], 1):
            scheme_details += f"**{i}. {scheme['name']}**\n"
            scheme_details += f"💰 **Benefits**: {scheme['benefits']}\n"
            scheme_details += f"✅ **Eligibility**: {scheme['eligibility']}\n"
            scheme_details += f"📋 **How to Apply**: {scheme['apply_process']}\n\n"
        
        return gemini_text + scheme_details
    
    def _filter_by_profile(self, schemes, profile):
        """Filter schemes based on farmer profile"""
        filtered_schemes = []
        
        for scheme in schemes:
            include_scheme = True
            
            # Filter by land size
            if profile.get('land_size'):
                land_size = float(profile['land_size'])
                eligibility_lower = scheme.get('eligibility', '').lower()
                
                if 'small' in eligibility_lower and land_size > 2:
                    include_scheme = False
                elif 'large' in eligibility_lower and land_size <= 2:
                    include_scheme = False
            
            # Filter by state
            if profile.get('state') and scheme.get('state_filter'):
                if scheme.get('state_filter').lower() != profile['state'].lower():
                    include_scheme = False
            
            if include_scheme:
                filtered_schemes.append(scheme)
        
        return filtered_schemes[:5]
    
    def _get_fallback_response(self, message, intent, schemes, profile):
        """Fallback response when Gemini API is not available"""
        response = ""
        
        # Add greeting based on intent
        greetings = {
            "insurance": "🛡️ **Crop Insurance Solutions**",
            "financial_support": "💰 **Financial Support Options**", 
            "irrigation": "💧 **Water Management Solutions**",
            "subsidy_development": "🚜 **Agriculture Development Programs**",
            "livestock_allied": "🐄 **Livestock & Fisheries Support**",
            "general": "🌾 **Comprehensive Agriculture Support**"
        }
        
        response += greetings.get(intent, greetings["general"]) + "\n\n"
        
        # Add scheme recommendations
        response += self._get_scheme_recommendations(intent, schemes, profile)
        
        # Add practical advice
        advice = self._get_practical_advice(message, intent, profile)
        if advice:
            response += "\n\n💡 **Practical Advice**\n" + advice
        
        # Add follow-up question
        response += "\n\n" + self._get_follow_up_question(intent)
        
        return response
    
    def _get_scheme_recommendations(self, intent, schemes, profile):
        """Get scheme recommendations"""
        if intent == "insurance":
            response = "🛡️ **Recommended Insurance Schemes**\n\n"
        elif intent == "financial_support":
            response = "💰 **Recommended Financial Schemes**\n\n"
        elif intent == "irrigation":
            response = "💧 **Recommended Irrigation Schemes**\n\n"
        elif intent == "subsidy_development":
            response = "🚜 **Recommended Development Schemes**\n\n"
        elif intent == "livestock_allied":
            response = "🐄 **Recommended Livestock Schemes**\n\n"
        else:
            response = "🌾 **Recommended Agriculture Schemes**\n\n"
        
        # Add top 3 schemes
        for i, scheme in enumerate(schemes[:3], 1):
            response += f"**{i}. {scheme['name']}**\n"
            response += f"💎 **Benefits**: {scheme['benefits']}\n"
            response += f"✅ **Eligibility**: {scheme['eligibility']}\n"
            response += f"📋 **Apply**: {scheme['apply_process']}\n\n"
        
        return response
    
    def _get_practical_advice(self, message, intent, profile):
        """Get practical farming advice"""
        advice_map = {
            "insurance": [
                "📸 Keep photos of crop damage and weather records",
                "📱 Download the Kisan Suvidha app for faster claim processing",
                "🏛️ Consider crop diversification to reduce insurance dependency"
            ],
            "financial_support": [
                "💳 Maintain good CIBIL score for better loan terms",
                "📊 Create a seasonal budget and track expenses",
                "🏦 Consider investing in farm equipment to increase productivity"
            ],
            "irrigation": [
                "💧 Use drip irrigation to save 30-50% water",
                "🌧 Test soil moisture before irrigation scheduling",
                "📅 Implement rainwater harvesting for dry periods"
            ],
            "subsidy_development": [
                "🚜 Choose equipment based on your land size and crop type",
                "📈 Study market trends before investing in new crops",
                "🔧 Regular equipment maintenance increases efficiency"
            ],
            "livestock_allied": [
                "🐄 Schedule regular veterinary checkups and vaccinations",
                "🌾 Store feed properly to maintain quality",
                "💧 Ensure clean drinking water for better animal health"
            ]
        }
        
        if intent in advice_map:
            return "\n".join(advice_map[intent])
        return "🌱 Always follow sustainable farming practices for long-term success."
    
    def _get_follow_up_question(self, intent):
        """Get contextual follow-up question"""
        questions = {
            "insurance": "Would you like me to help you with the insurance claim process?",
            "financial_support": "Do you need information about crop loans or income support schemes?",
            "irrigation": "Would you like details about water conservation techniques?",
            "subsidy_development": "Are you interested in knowing about equipment subsidies in your area?",
            "livestock_allied": "Do you need guidance about livestock management practices?",
            "general": "How can I assist you further with your farming needs?"
        }
        
        return questions.get(intent, questions["general"])

# Test the Gemini chatbot
if __name__ == "__main__":
    bot = GeminiAgricultureBot()
    
    # Test messages
    test_messages = [
        "I need crop insurance for my wheat farm",
        "How can I get financial support for my farm?",
        "What irrigation schemes are available for small farmers?",
        "Tell me about livestock development schemes"
    ]
    
    print("Testing Gemini Agriculture Bot")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response = bot.get_response(message)
        print(f"\nAgriSahayak AI: {response.encode('ascii', 'ignore').decode('ascii')}")
        print("-" * 50)
