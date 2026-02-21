#!/usr/bin/env python3
"""
Concise AI Agriculture Assistant
Short, clear, farmer-friendly responses
"""

import google.generativeai as genai
import json
import random
from datetime import datetime
from schemes_database import schemes_database, intent_keywords, detect_intent, get_schemes_by_intent, get_all_schemes
from translations import translations

class ConciseAIChatbot:
    def __init__(self, language='en'):
        self.language = language
        self.t = translations[language]
        
        # Gemini API Keys
        self.gemini_api_keys = [
            "AIzaSyDg5T18bwuIzk8n-YDgfhqyEkVup88iZtY",
            "AIzaSyDUJepqmkCUrK0fZXJ62gNA6iwpCRadzc8"
        ]
        self.current_key_index = 0
        
        # Conversation context
        self.last_intent = None
        self.last_schemes = []
        
        # Initialize Gemini
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
        """Generate short, clear response"""
        try:
            # Detect intent
            intent = detect_intent(message)
            
            # Get relevant schemes
            if intent != "general":
                relevant_schemes = get_schemes_by_intent(intent)
            else:
                relevant_schemes = get_all_schemes()
            
            # Filter schemes based on farmer profile
            if farmer_profile:
                relevant_schemes = self._filter_by_profile(relevant_schemes, farmer_profile)
            
            # Store for context
            self.last_intent = intent
            self.last_schemes = relevant_schemes[:3]
            
            # Try Gemini first for natural conversation
            if self.api_working and not self._is_apply_request(message):
                gemini_response = self._get_gemini_response(message, intent, relevant_schemes, farmer_profile)
                if gemini_response and len(gemini_response.strip()) > 10:
                    return gemini_response
            
            # Fallback to concise responses
            return self._get_concise_response(message, intent, relevant_schemes, farmer_profile)
            
        except Exception as e:
            print(f"Error generating response: {e}")
            if self._switch_api_key():
                return self.get_response(message, farmer_profile)
            else:
                return self._get_concise_response(message, intent, relevant_schemes, farmer_profile)
    
    def _is_apply_request(self, message):
        """Check if user wants to apply for scheme"""
        apply_keywords = ['apply', 'application', 'register', 'enroll', 'sign up']
        return any(keyword in message.lower() for keyword in apply_keywords)
    
    def _get_gemini_response(self, message, intent, schemes, profile):
        """Get short Gemini response"""
        try:
            prompt = f"""
You are AgriSahayak AI - help farmers with SHORT, SIMPLE answers.

User: "{message}"
Intent: {intent}
Profile: {json.dumps(profile, indent=2) if profile else 'None'}

Available Schemes: {json.dumps(schemes[:2], indent=2)}

RESPONSE RULES:
1. Keep answers VERY SHORT (2-3 sentences max)
2. Use simple language farmers understand
3. Recommend only 1-2 best schemes
4. Be direct and helpful
5. No long explanations
6. Use 1-2 emojis maximum

Respond in {self.language.upper()} language.
"""
            
            response = self.gemini_model.generate_content(prompt)
            if response.text and len(response.text.strip()) > 5:
                return self._format_concise_response(response.text, schemes[:2])
            return None
            
        except Exception as e:
            print(f"Gemini error: {e}")
            return None
    
    def _format_concise_response(self, ai_text, schemes):
        """Format AI response with scheme details"""
        # Add just 2 schemes with minimal details
        if schemes:
            scheme_section = "\n\n**Best Schemes for You:**\n"
            for i, scheme in enumerate(schemes[:2], 1):
                scheme_section += f"\n{i}. **{scheme['name']}**\n"
                scheme_section += f"📋 {scheme['apply_process']}\n"
            return ai_text + scheme_section
        return ai_text
    
    def _get_concise_response(self, message, intent, schemes, profile):
        """Generate concise response"""
        
        # Handle apply requests
        if self._is_apply_request(message):
            return self._handle_apply_request()
        
        # Handle yes/no responses
        if message.lower() in ['yes', 'haan', 'ho']:
            return self._handle_positive_response()
        
        # Get short response based on intent
        responses = {
            "insurance": [
                "🛡️ **Crop Insurance Schemes Available**\n\n1. **PMFBY** - Protects crops from natural damage\n2. **WBCIS** - Weather-based automatic claims\n\nBoth schemes cover your crops. Need help with documents?",
                "🌾 **Insurance for Your Crops**\n\n**PMFBY** and **WBCIS** are best for crop protection.\n\nPMFBY covers all crop damage, WBCIS gives automatic payment for bad weather.\n\nWhich interests you more?"
            ],
            "financial_support": [
                "💰 **Financial Help Available**\n\n1. **PM-KISAN** - ₹6,000 yearly direct support\n2. **KCC** - Low interest crop loans\n\nBoth help small farmers. Which do you need?",
                "💵 **Money Support Schemes**\n\n**PM-KISAN** gives ₹6,000 per year.\n\n**KCC** provides cheap loans for farming.\n\nWant to apply for either?"
            ],
            "irrigation": [
                "💧 **Water Schemes for You**\n\n1. **PMKSY** - Help for irrigation equipment\n2. **PDMC** - 55% subsidy for drip irrigation\n\nSave water and money. Need details?",
                "🚰 **Irrigation Support**\n\n**PMKSY** helps buy irrigation equipment.\n\n**PDMC** gives big subsidy for drip systems.\n\nWhich helps your farm more?"
            ],
            "subsidy_development": [
                "🚜 **Farm Equipment Help**\n\n1. **SMAM** - 50% subsidy on machinery\n2. **RKVY** - Farm development support\n\nModern equipment available. Want to know more?",
                "⚙️ **Equipment Subsidies**\n\n**SMAM** gives 50% off on farm machines.\n\n**RKVY** supports farm improvements.\n\nWhat equipment do you need?"
            ],
            "livestock_allied": [
                "🐄 **Livestock Schemes**\n\n1. **National Livestock Mission** - Animal health support\n2. **Dairy Development** - Help for dairy farmers\n\nBetter animal care available. Need details?",
                "📋 **Animal Husbandry Help**\n\n**Livestock Mission** supports animal health.\n\n**Dairy schemes** help milk production.\n\nWhich animals do you have?"
            ]
        }
        
        if intent in responses:
            return random.choice(responses[intent])
        
        # General response
        general_responses = [
            "🌾 **I can help with farming schemes!**\n\nTell me what you need:\n• Crop insurance\n• Financial support\n• Irrigation help\n• Equipment subsidy\n• Livestock schemes\n\nWhat interests you?",
            "👨‍🌾 **Hello! I'm here to help farmers.**\n\nI can assist with:\n• Insurance schemes\n• Financial help\n• Water management\n• Farm equipment\n• Animal husbandry\n\nWhat do you need help with?"
        ]
        
        return random.choice(general_responses)
    
    def _handle_apply_request(self):
        """Handle application requests"""
        if self.last_schemes:
            scheme = self.last_schemes[0]
            return f"📋 **Apply for {scheme['name']}**\n\n**Steps:**\n1. {scheme['apply_process']}\n2. Submit required documents\n3. Wait for approval\n\nNeed help with documents?"
        return "📋 **Application Help**\n\nTell me which scheme you want to apply for, and I'll guide you step by step."
    
    def _handle_positive_response(self):
        """Handle positive responses"""
        if self.last_intent == "insurance":
            return "📄 **Documents needed:**\n• Aadhaar card\n• Land records\n• Bank details\n• Crop details\n\nI can help you prepare these. What's your land size?"
        elif self.last_intent == "financial_support":
            return "📄 **Documents needed:**\n• Aadhaar card\n• Land papers\n• Bank account\n• Income proof\n\nReady to apply? I'll guide you."
        else:
            return "👍 **Great!** I'll help you step by step.\n\nFirst, tell me your land size and location for better guidance."
    
    def _filter_by_profile(self, schemes, profile):
        """Filter schemes based on profile"""
        filtered_schemes = []
        
        for scheme in schemes:
            include_scheme = True
            
            if profile.get('land_size'):
                land_size = float(profile['land_size'])
                eligibility_lower = scheme.get('eligibility', '').lower()
                
                if 'small' in eligibility_lower and land_size > 2:
                    include_scheme = False
                elif 'large' in eligibility_lower and land_size <= 2:
                    include_scheme = False
            
            if include_scheme:
                filtered_schemes.append(scheme)
        
        return filtered_schemes[:3]

# Test the concise chatbot
if __name__ == "__main__":
    bot = ConciseAIChatbot()
    
    # Test messages
    test_messages = [
        "I need crop insurance",
        "apply me for the scheme",
        "yes",
        "What financial schemes are there?",
        "help with irrigation"
    ]
    
    print("Testing Concise AI Agriculture Bot")
    print("=" * 40)
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response = bot.get_response(message, {'name': 'Ramesh', 'land_size': '2'})
        print(f"AI: {response.encode('ascii', 'ignore').decode('ascii')}")
        print("-" * 40)
