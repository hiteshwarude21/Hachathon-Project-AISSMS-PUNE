#!/usr/bin/env python3
"""
Advanced AI Agriculture Assistant with True Gemini Integration
Dynamic, conversational AI responses with context awareness
"""

import google.generativeai as genai
import json
import random
from datetime import datetime
from schemes_database import schemes_database, intent_keywords, detect_intent, get_schemes_by_intent, get_all_schemes
from translations import translations

class AdvancedAIChatbot:
    def __init__(self, language='en'):
        self.language = language
        self.t = translations[language]
        
        # Gemini API Keys - Using both for load balancing and fallback
        self.gemini_api_keys = [
            "AIzaSyDg5T18bwuIzk8n-YDgfhqyEkVup88iZtY",
            "AIzaSyDUJepqmkCUrK0fZXJ62gNA6iwpCRadzc8"
        ]
        self.current_key_index = 0
        
        # Conversation context for better responses
        self.conversation_history = []
        self.user_context = {}
        
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
        """Generate truly intelligent response using Gemini AI"""
        try:
            # Update conversation context
            self._update_conversation_context(message, farmer_profile)
            
            # Detect intent
            intent = detect_intent(message)
            
            # Get relevant schemes
            if intent != "general":
                relevant_schemes = get_schemes_by_intent(intent)
            else:
                relevant_schemes = get_all_schemes()
            
            # Filter schemes based on farmer profile if available
            if farmer_profile:
                relevant_schemes = self._filter_by_profile(relevant_schemes, farmer_profile)
            
            # Try to get Gemini response first
            if self.api_working:
                gemini_response = self._get_gemini_response(message, intent, relevant_schemes, farmer_profile)
                if gemini_response and len(gemini_response.strip()) > 50:  # Ensure meaningful response
                    return gemini_response
            
            # Fallback to enhanced rule-based response
            return self._get_enhanced_fallback_response(message, intent, relevant_schemes, farmer_profile)
            
        except Exception as e:
            print(f"Error generating response: {e}")
            # Try switching API key and retry once
            if self._switch_api_key():
                return self.get_response(message, farmer_profile)
            else:
                return self._get_enhanced_fallback_response(message, intent, relevant_schemes, farmer_profile)
    
    def _update_conversation_context(self, message, farmer_profile):
        """Update conversation context for better responses"""
        # Add to conversation history (keep last 5 messages)
        self.conversation_history.append({
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'profile': farmer_profile
        })
        
        # Keep only last 5 messages for context
        if len(self.conversation_history) > 5:
            self.conversation_history = self.conversation_history[-5:]
        
        # Update user context
        if farmer_profile:
            self.user_context.update(farmer_profile)
    
    def _get_gemini_response(self, message, intent, schemes, profile):
        """Generate dynamic response using Gemini AI"""
        try:
            # Create comprehensive, context-aware prompt
            prompt = self._create_dynamic_prompt(message, intent, schemes, profile)
            
            # Generate response with Gemini
            response = self.gemini_model.generate_content(prompt)
            
            if response.text and len(response.text.strip()) > 20:
                return self._format_ai_response(response.text, intent, schemes)
            else:
                return None
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    def _create_dynamic_prompt(self, message, intent, schemes, profile):
        """Create a dynamic, conversational prompt for Gemini"""
        
        # Build conversation context
        context_summary = ""
        if len(self.conversation_history) > 1:
            context_summary = "Recent conversation: " + "; ".join([h['message'] for h in self.conversation_history[-3:]])
        
        # Create personalized prompt
        prompt = f"""
You are AgriSahayak AI, an intelligent agricultural assistant helping Indian farmers. Be conversational, empathetic, and provide personalized advice.

CURRENT QUERY: "{message}"
USER INTENT: {intent}
FARMER PROFILE: {json.dumps(profile, indent=2) if profile else 'New user, no profile yet'}
{context_summary}

AVAILABLE GOVERNMENT SCHEMES:
{json.dumps(schemes[:3], indent=2)}

RESPONSE GUIDELINES:
1. Be conversational and natural, not robotic
2. Address the farmer by name if available in profile
3. Provide specific, actionable advice related to their query
4. Recommend 2-3 most relevant schemes with personalized explanations
5. Include practical farming tips based on their situation
6. Ask follow-up questions to understand their needs better
7. Use emojis naturally to make responses friendly
8. Keep responses comprehensive but not too long
9. If they mention specific crops, locations, or problems, reference them specifically
10. End with an encouraging message and clear next steps

RESPOND IN {self.language.upper()} LANGUAGE.
"""
        return prompt
    
    def _format_ai_response(self, ai_text, intent, schemes):
        """Format AI response to include scheme details and apply button functionality"""
        # Add scheme details section for apply button functionality
        scheme_section = "\n\n🎯 **Recommended Government Schemes for You**\n\n"
        
        for i, scheme in enumerate(schemes[:3], 1):
            scheme_section += f"**{i}. {scheme['name']}**\n"
            scheme_section += f"💰 **Benefits**: {scheme['benefits']}\n"
            scheme_section += f"✅ **Eligibility**: {scheme['eligibility']}\n"
            scheme_section += f"📋 **Application**: {scheme['apply_process']}\n\n"
        
        # Combine AI response with scheme information
        full_response = ai_text + scheme_section
        
        return full_response
    
    def _filter_by_profile(self, schemes, profile):
        """Enhanced filtering based on farmer profile"""
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
    
    def _get_enhanced_fallback_response(self, message, intent, schemes, profile):
        """Enhanced fallback response with more variety"""
        
        # Dynamic greeting based on time and context
        hour = datetime.now().hour
        if hour < 12:
            greeting = "🌅 Good morning"
        elif hour < 17:
            greeting = "☀️ Good afternoon"
        else:
            greeting = "🌆 Good evening"
        
        # Personalize greeting
        if profile and profile.get('name'):
            greeting += f" {profile['name']}!"
        else:
            greeting += " farmer friend!"
        
        response = f"{greeting}\n\n"
        
        # Add contextual opening
        response += self._get_contextual_opening(message, intent, profile)
        
        # Add scheme recommendations
        response += self._get_dynamic_scheme_recommendations(intent, schemes, profile)
        
        # Add personalized advice
        response += self._get_personalized_advice(message, intent, profile)
        
        # Add engaging follow-up
        response += "\n\n" + self._get_engaging_follow_up(intent, profile)
        
        return response
    
    def _get_contextual_opening(self, message, intent, profile):
        """Get contextual opening based on message and profile"""
        message_lower = message.lower()
        
        if 'help' in message_lower or 'confused' in message_lower:
            return "I'm here to help you navigate through the best agricultural schemes and support available. Let me guide you step by step."
        elif 'urgent' in message_lower or 'immediately' in message_lower:
            return "I understand this is urgent for you. Let me quickly provide you with the most relevant options."
        elif profile and profile.get('land_size'):
            return f"Based on your {profile['land_size']} hectares of land, I've found some perfect matches for you."
        else:
            return "I'll help you find the best agricultural schemes and support for your farming needs."
    
    def _get_dynamic_scheme_recommendations(self, intent, schemes, profile):
        """Get dynamic scheme recommendations"""
        if intent == "insurance":
            response = "🛡️ **To protect your crops from uncertainties, these insurance schemes are perfect:**\n\n"
        elif intent == "financial_support":
            response = "💰 **For financial growth and stability, consider these options:**\n\n"
        elif intent == "irrigation":
            response = "💧 **To ensure proper water management for your crops:**\n\n"
        elif intent == "subsidy_development":
            response = "🚜 **For modern farming equipment and development:**\n\n"
        elif intent == "livestock_allied":
            response = "🐄 **For livestock and allied activities:**\n\n"
        else:
            response = "🌾 **Here are some excellent schemes for your farming journey:**\n\n"
        
        # Add schemes with personalized details
        for i, scheme in enumerate(schemes[:3], 1):
            response += f"**{i}. {scheme['name']}**\n"
            
            # Personalize benefits based on profile
            benefits = scheme['benefits']
            if profile and profile.get('land_size') and float(profile['land_size']) <= 2:
                benefits += " (Perfect for small farmers like you!)"
            
            response += f"💎 **Why this is great for you**: {benefits}\n"
            response += f"✅ **You're eligible if**: {scheme['eligibility']}\n"
            response += f"📋 **How to get started**: {scheme['apply_process']}\n\n"
        
        return response
    
    def _get_personalized_advice(self, message, intent, profile):
        """Get personalized advice based on context"""
        message_lower = message.lower()
        
        advice_map = {
            "insurance": [
                "📸 Keep your phone ready to photograph any crop damage immediately",
                "📱 Download the Kisan Suvidha app - it's a lifesaver during claim time",
                "🌾 Consider crop rotation to reduce risks and insurance dependency"
            ],
            "financial_support": [
                "💳 Keep your bank statements organized - they help with loan applications",
                "📊 Track your farming expenses monthly - it helps in financial planning",
                "🏦 Build a good relationship with your local bank branch manager"
            ],
            "irrigation": [
                "💧 Drip irrigation can save you 30-50% on water bills",
                "🌧 Check soil moisture before watering - overwatering harms crops",
                "📅 Start rainwater harvesting - it's free water for dry periods"
            ],
            "subsidy_development": [
                "🚜 Choose equipment that matches your land size - bigger isn't always better",
                "📈 Visit nearby farms to see what equipment works best in your area",
                "🔧 Regular maintenance prevents costly breakdowns during peak season"
            ],
            "livestock_allied": [
                "🐄 Schedule monthly vet checkups - prevention is cheaper than cure",
                "🌾 Store feed in dry areas to prevent mold and spoilage",
                "💧 Clean water increases animal productivity significantly"
            ]
        }
        
        if intent in advice_map:
            advice = random.choice(advice_map[intent])  # Randomize advice for variety
            return f"💡 **Quick Tip**: {advice}"
        
        return "💡 **Quick Tip**: Always stay updated with the latest agricultural practices and government schemes."
    
    def _get_engaging_follow_up(self, intent, profile):
        """Get engaging follow-up questions"""
        follow_ups = {
            "insurance": [
                "Would you like me to explain the claim process step by step?",
                "Do you have questions about which crops are covered?",
                "Should I help you prepare the documents needed?"
            ],
            "financial_support": [
                "Are you looking for immediate funds or long-term investment support?",
                "Would you like to know about interest subsidies available?",
                "Should I guide you through the loan application process?"
            ],
            "irrigation": [
                "Would you like specific tips for your crop type?",
                "Are you interested in knowing about government subsidies for pumps?",
                "Should I help you calculate water requirements for your land?"
            ],
            "subsidy_development": [
                "Which type of equipment are you most interested in?",
                "Would you like to know about custom hiring centers in your area?",
                "Should I help you compare different equipment options?"
            ],
            "livestock_allied": [
                "What type of animals are you planning to raise?",
                "Would you like information about animal health programs?",
                "Should I help you find veterinary services nearby?"
            ]
        }
        
        if intent in follow_ups:
            return random.choice(follow_ups[intent])
        
        return "What specific aspect of farming would you like to explore next? I'm here to help!"

# Test the advanced AI chatbot
if __name__ == "__main__":
    bot = AdvancedAIChatbot()
    
    # Test messages
    test_messages = [
        "I need help with crop insurance for my 2-hectare wheat farm",
        "Can you suggest financial schemes for small farmers?",
        "What irrigation options work best for sandy soil?",
        "Tell me about livestock schemes for dairy farming"
    ]
    
    print("Testing Advanced AI Agriculture Bot")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response = bot.get_response(message, {'name': 'Ramesh', 'land_size': '2', 'state': 'Maharashtra'})
        print(f"\nAI Assistant: {response.encode('ascii', 'ignore').decode('ascii')}")
        print("-" * 50)
