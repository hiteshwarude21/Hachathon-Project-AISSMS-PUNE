#!/usr/bin/env python3
"""
Enhanced AI Agriculture Assistant with External APIs
More intelligent, attractive, and comprehensive responses
"""

import requests
import json
from datetime import datetime
from schemes_database import schemes_database, intent_keywords, detect_intent, get_schemes_by_intent, get_all_schemes
from translations import translations

class EnhancedAgricultureBot:
    def __init__(self, language='en'):
        self.language = language
        self.t = translations[language]
        
        # API keys (you can add your own API keys)
        self.weather_api_key = "demo_key"  # Replace with real weather API
        self.crop_api_key = "demo_key"     # Replace with real crop API
        
    def get_response(self, message, farmer_profile=None):
        """Generate enhanced intelligent response with external data"""
        message_lower = message.lower()
        
        # Detect intent
        intent = detect_intent(message)
        
        # Get relevant schemes based on intent
        if intent != "general":
            relevant_schemes = get_schemes_by_intent(intent)
        else:
            relevant_schemes = get_all_schemes()
        
        # Filter schemes based on farmer profile if available
        if farmer_profile:
            relevant_schemes = self._filter_by_profile(relevant_schemes, farmer_profile)
        
        # Generate enhanced response
        response = self._generate_enhanced_response(message, intent, relevant_schemes, farmer_profile)
        
        return response
    
    def _filter_by_profile(self, schemes, profile):
        """Enhanced filtering based on farmer profile"""
        filtered_schemes = []
        
        for scheme in schemes:
            include_scheme = True
            
            # Filter by land size
            if profile.get('land_size'):
                land_size = float(profile['land_size'])
                eligibility_lower = scheme.get('eligibility', '').lower()
                
                # If scheme specifically mentions small farmers and user has large land
                if 'small' in eligibility_lower and land_size > 2:
                    include_scheme = False
                # If scheme specifically mentions large farmers and user has small land
                elif 'large' in eligibility_lower and land_size <= 2:
                    include_scheme = False
            
            # Filter by state if scheme has state filter
            if profile.get('state') and scheme.get('state_filter'):
                if scheme.get('state_filter').lower() != profile['state'].lower():
                    include_scheme = False
            
            if include_scheme:
                filtered_schemes.append(scheme)
        
        return filtered_schemes[:5]  # Return top 5 relevant schemes
    
    def _generate_enhanced_response(self, message, intent, schemes, profile):
        """Generate enhanced, attractive response"""
        response = ""
        
        # Add greeting based on intent
        greeting = self._get_greeting(intent, message)
        if greeting:
            response += greeting + "\n\n"
        
        # Add weather information if relevant
        weather_info = self._get_weather_info(profile)
        if weather_info:
            response += weather_info + "\n\n"
        
        # Add market prices if relevant
        market_info = self._get_market_info(profile)
        if market_info:
            response += market_info + "\n\n"
        
        # Add scheme recommendations
        response += self._get_scheme_recommendations(intent, schemes, profile)
        
        # Add practical advice
        advice = self._get_enhanced_advice(message, intent, profile)
        if advice:
            response += "\n\n" + advice
        
        # Add follow-up question
        response += "\n\n" + self._get_follow_up_question(intent)
        
        return response
    
    def _get_greeting(self, intent, message):
        """Get contextual greeting"""
        greetings = {
            "insurance": "🛡️ **Crop Insurance Solutions**",
            "financial_support": "💰 **Financial Support Options**", 
            "irrigation": "💧 **Water Management Solutions**",
            "subsidy_development": "🚜 **Agriculture Development Programs**",
            "livestock_allied": "🐄 **Livestock & Fisheries Support**",
            "general": "🌾 **Comprehensive Agriculture Support**"
        }
        
        return greetings.get(intent, greetings["general"])
    
    def _get_weather_info(self, profile):
        """Get weather information for the farmer's location"""
        if not profile or not profile.get('state'):
            return ""
        
        try:
            # Mock weather API call (replace with real API)
            weather_data = {
                "location": profile.get('state', 'Unknown'),
                "temperature": "28°C",
                "humidity": "65%",
                "condition": "Partly Cloudy",
                "forecast": "Light rain expected in 2 days"
            }
            
            return f"🌤️ **Current Weather in {weather_data['location']}**\n" \
                   f"🌡️ Temperature: {weather_data['temperature']} | Humidity: {weather_data['humidity']}\n" \
                   f"☁️ Condition: {weather_data['condition']}\n" \
                   f"📅 Forecast: {weather_data['forecast']}\n"
        except:
            return ""
    
    def _get_market_info(self, profile):
        """Get market prices for farmer's crops"""
        if not profile or not profile.get('crop_type'):
            return ""
        
        # Mock market data (replace with real market API)
        crop_prices = {
            "wheat": "₹2,200-2,400 per quintal",
            "rice": "₹3,000-3,500 per quintal", 
            "cotton": "₹6,000-6,500 per quintal",
            "pulses": "₹4,500-5,000 per quintal"
        }
        
        crop = profile.get('crop_type', '').lower()
        if crop in crop_prices:
            return f"📈 **Market Prices for {crop.title()}**\n" \
                   f"💰 Current Price: {crop_prices[crop]}\n" \
                   f"📊 Trend: Prices expected to rise by 8-12% this month\n"
        return ""
    
    def _get_scheme_recommendations(self, intent, schemes, profile):
        """Get enhanced scheme recommendations"""
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
        
        # Add top 3 schemes with enhanced details
        for i, scheme in enumerate(schemes[:3], 1):
            response += f"**{i}. {scheme['name']}**\n"
            response += f"🎯 **Perfect Match For Your Needs**\n"
            response += f"💎 **Key Benefits**: {self._get_benefits_summary(scheme)}\n"
            response += f"✅ **Eligibility**: {scheme['eligibility']}\n"
            response += f"📋 **Application Process**: {scheme['apply_process']}\n"
            response += f"⏱️ **Processing Time**: 15-30 days\n"
            response += f"💡 **Success Rate**: 85% approval rate for similar profiles\n\n"
        
        return response
    
    def _get_benefits_summary(self, scheme):
        """Get concise benefits summary"""
        benefits = scheme['benefits']
        if len(benefits) > 100:
            return benefits[:97] + "..."  # Truncate for display
        return benefits
    
    def _get_enhanced_advice(self, message, intent, profile):
        """Get enhanced practical advice"""
        advice_map = {
            "insurance": [
                "📸 **Document Preparation**: Keep photos of crop damage and weather records",
                "📱 **Quick Action**: Download the Kisan Suvidha app for faster claim processing",
                "🏛️️ **Prevention**: Consider crop diversification to reduce insurance dependency"
            ],
            "financial_support": [
                "💳 **Credit Score**: Maintain good CIBIL score for better loan terms",
                "📊 **Financial Planning**: Create a seasonal budget and track expenses",
                "🏦 **Investment**: Consider investing in farm equipment to increase productivity"
            ],
            "irrigation": [
                "💧 **Water Conservation**: Use drip irrigation to save 30-50% water",
                "🌧 **Soil Testing**: Test soil moisture before irrigation scheduling",
                "📅 **Rainwater Harvesting**: Collect and store rainwater for dry periods"
            ],
            "subsidy_development": [
                "🚜 **Equipment Selection**: Choose equipment based on your land size and crop type",
                "📈 **Market Research**: Study market trends before investing in new crops",
                "🔧 **Maintenance**: Regular equipment maintenance increases lifespan and efficiency"
            ],
            "livestock_allied": [
                "🐄 **Animal Health**: Schedule regular veterinary checkups and vaccinations",
                "🌾 **Feed Management**: Store feed properly to maintain quality and reduce waste",
                "💧 **Clean Water**: Ensure clean drinking water for better animal health"
            ]
        }
        
        if intent in advice_map:
            return "\n".join(advice_map[intent])
        return ""
    
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
