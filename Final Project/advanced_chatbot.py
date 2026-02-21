#!/usr/bin/env python3
"""
Advanced AI Agriculture Assistant
Intelligent multi-scheme recommendation system with intent detection
"""

from schemes_database import schemes_database, intent_keywords, detect_intent, get_schemes_by_intent, get_all_schemes
from translations import translations

class AdvancedAgricultureBot:
    def __init__(self, language='en'):
        self.language = language
        self.t = translations[language]
        
    def get_response(self, message, farmer_profile=None):
        """Generate intelligent response based on user message and profile"""
        message_lower = message.lower()
        
        # Detect intent
        intent = detect_intent(message)
        
        # Get relevant schemes based on intent
        if intent != "general":
            relevant_schemes = get_schemes_by_intent(intent)
        else:
            relevant_schemes = get_all_schemes()
        
        # Filter schemes based on farmer profile if available (but ensure we always have schemes)
        if farmer_profile and relevant_schemes:
            filtered_schemes = self._filter_by_profile(relevant_schemes, farmer_profile)
            if filtered_schemes:  # Only use filtered if we have results
                relevant_schemes = filtered_schemes
        
        # Ensure we have at least 3 schemes
        if len(relevant_schemes) < 3:
            all_schemes = get_all_schemes()
            # Add schemes from other categories to reach minimum 3
            for scheme in all_schemes:
                if scheme not in relevant_schemes:
                    relevant_schemes.append(scheme)
                    if len(relevant_schemes) >= 3:
                        break
        
        # Generate response
        response = self._generate_response(message, intent, relevant_schemes, farmer_profile)
        
        return response
    
    def _filter_by_profile(self, schemes, profile):
        """Filter schemes based on farmer profile"""
        filtered_schemes = []
        
        for scheme in schemes:
            # Always include the scheme unless there's a strong reason not to
            include_scheme = True
            
            # Filter by land size only if it's explicitly mentioned in eligibility
            if profile.get('land_size'):
                land_size = float(profile['land_size'])
                eligibility_lower = scheme.get('eligibility', '').lower()
                
                # If scheme specifically mentions small farmers and user has large land
                if 'small' in eligibility_lower and land_size > 2:
                    include_scheme = False
                # If scheme specifically mentions large farmers and user has small land
                elif 'large' in eligibility_lower and land_size <= 2:
                    include_scheme = False
            
            if include_scheme:
                filtered_schemes.append(scheme)
        
        return filtered_schemes
    
    def _generate_response(self, message, intent, schemes, profile):
        """Generate contextual response"""
        if self.language == 'en':
            return self._generate_english_response(message, intent, schemes, profile)
        elif self.language == 'hi':
            return self._generate_hindi_response(message, intent, schemes, profile)
        else:  # Marathi
            return self._generate_marathi_response(message, intent, schemes, profile)
    
    def _generate_english_response(self, message, intent, schemes, profile):
        """Generate response in English"""
        response = ""
        
        if intent == "insurance":
            response = "🛡️ **Crop Insurance Schemes Available**\n\n"
        elif intent == "financial_support":
            response = "💰 **Financial Support Schemes Available**\n\n"
        elif intent == "irrigation":
            response = "💧 **Irrigation & Water Management Schemes**\n\n"
        elif intent == "subsidy_development":
            response = "🚜 **Agriculture Development & Equipment Schemes**\n\n"
        elif intent == "livestock_allied":
            response = "🐄 **Livestock & Fisheries Schemes**\n\n"
        else:  # general case
            response = "🌾 **Multiple Agriculture Schemes Available**\n\n"
        
        # Add scheme recommendations (minimum 3) - simplified format
        for i, scheme in enumerate(schemes[:3], 1):
            response += f"**{i}. {scheme['name']}**\n"
            response += f"Benefits: {scheme['benefits']}\n"
            response += f"Eligibility: {scheme['eligibility']}\n"
            response += f"Apply: {scheme['apply_process']}\n\n"
        
        # Add practical advice if needed
        advice = self._get_practical_advice(message, intent)
        if advice:
            response += f"💡 **Additional Advice**: {advice}\n\n"
        
        response += "Would you like to apply for any of these schemes?"
        
        return response
    
    def _generate_hindi_response(self, message, intent, schemes, profile):
        """Generate response in Hindi"""
        response = ""
        
        if intent == "insurance":
            response = "🛡️ **उपलब्ध फसल बीमा योजनाएँ**\n\n"
        elif intent == "financial_support":
            response = "💰 **उपलब्ध वित्तीय सहायता योजनाएँ**\n\n"
        elif intent == "irrigation":
            response = "💧 **सिंचाई और जल प्रबंधन योजनाएँ**\n\n"
        elif intent == "subsidy_development":
            response = "🚜 **कृषि विकास और उपकरण योजनाएँ**\n\n"
        elif intent == "livestock_allied":
            response = "🐄 **पशुधन और मत्स्य पालन योजनाएँ**\n\n"
        else:
            response = "🌾 **एकाधिक कृषि योजनाएँ उपलब्ध**\n\n"
        
        # Add scheme recommendations - simplified format
        for i, scheme in enumerate(schemes[:3], 1):
            response += f"**{i}. {scheme['name']}**\n"
            response += f"लाभ: {scheme['benefits']}\n"
            response += f"पात्रता: {scheme['eligibility']}\n"
            response += f"आवेदन: {scheme['apply_process']}\n\n"
        
        # Add practical advice
        advice = self._get_practical_advice_hindi(message, intent)
        if advice:
            response += f"💡 **अतिरिक्त सलाह*: {advice}\n\n"
        
        response += "क्या आप इनमें से किसी योजना के लिए आवेदन करना चाहेंगे?"
        
        return response
    
    def _generate_marathi_response(self, message, intent, schemes, profile):
        """Generate response in Marathi"""
        response = ""
        
        if intent == "insurance":
            response = "🛡️ **उपलब्ध पिकांचे विमा योजना**\n\n"
        elif intent == "financial_support":
            response = "💰 **आर्थिक मदत योजना**\n\n"
        elif intent == "irrigation":
            response = "💧 **सिंचाई आणि जल व्यवस्थापन योजना**\n\n"
        elif intent == "subsidy_development":
            response = "🚜 **शेती विकास आणि उपकरणे योजना**\n\n"
        elif intent == "livestock_allied":
            response = "🐄 **पशुधन आणि मत्स्य पालन योजना**\n\n"
        else:
            response = "🌾 **एकाधिक शेती योजना उपलब्ध**\n\n"
        
        # Add scheme recommendations - simplified format
        for i, scheme in enumerate(schemes[:3], 1):
            response += f"**{i}. {scheme['name']}**\n"
            response += f"फायदे: {scheme['benefits']}\n"
            response += f"पात्रता: {scheme['eligibility']}\n"
            response += f"अर्ज कसा: {scheme['apply_process']}\n\n"
        
        # Add practical advice
        advice = self._get_practical_advice_marathi(message, intent)
        if advice:
            response += f"💡 **अतिरिक्त सल्ला**: {advice}\n\n"
        
        response += "तुम्ही यापैका कोणत्या योजनांसाठी अर्ज करू इच्छित का?"
        
        return response
    
    def _get_reason(self, scheme, intent, profile):
        """Get reason for scheme recommendation"""
        if intent == "insurance":
            return "Protects your crops from natural calamities and financial losses"
        elif intent == "financial_support":
            return "Provides direct financial assistance and credit facilities"
        elif intent == "irrigation":
            return "Helps improve water management and crop productivity"
        elif intent == "subsidy_development":
            return "Supports modern farming equipment and infrastructure"
        elif intent == "livestock_allied":
            return "Promotes animal husbandry and allied activities"
        else:
            return "Comprehensive support for agricultural development"
    
    def _get_reason_hindi(self, scheme, intent, profile):
        """Get reason for scheme recommendation in Hindi"""
        if intent == "insurance":
            return "प्राकृतिक आपदाओं और वित्तीय हानि से आपकी फसलों की रक्षा करता है"
        elif intent == "financial_support":
            return "प्रत्यक्ष वित्तीय सहायता और ऋण सुविधाएँ प्रदान करता है"
        elif intent == "irrigation":
            return "जल प्रबंधन और फसल उत्पादनक्षमता में सुधार करने में मदद करता है"
        elif intent == "subsidy_development":
            return "आधुनिक खेती उपकरण और बुनियादी का समर्थन करता है"
        elif intent == "livestock_allied":
            return "पशुधन और संबंधित गतिविधियों को बढ़ावा देता है"
        else:
            return "कृषि विकास के लिए व्यापक समर्थन"
    
    def _get_reason_marathi(self, scheme, intent, profile):
        """Get reason for scheme recommendation in Marathi"""
        if intent == "insurance":
            return "नैसर्गिक आपत्ती आणि आर्थिक नुकसानापासून तुमच्या पिकांचे रक्षण करते"
        elif intent == "financial_support":
            return "थेट प्रत्यक्ष आर्थिक मदत आणि कर्ज सुविधा प्रदान करते"
        elif intent == "irrigation":
            return "जल व्यवस्थापन आणि पिकांच्या उत्पादनक्षमता सुधारण्यात मदत करते"
        elif intent == "subsidy_development":
            return "आधुनिक शेती उपकरणे आणि संरचनाचे समर्थन करते"
        elif intent == "livestock_allied":
            return "पशुधन आणि संबंधित क्रियांना वाढ देते"
        else:
            return "शेती विकासासाठी व्यापक समर्थन"
    
    def _get_practical_advice(self, message, intent):
        """Get practical farming advice"""
        message_lower = message.lower()
        
        if "water" in message_lower or "irrigation" in message_lower:
            return "Consider drip irrigation to save 30-50% water compared to flood irrigation. Mulching also helps retain soil moisture."
        elif "disease" in message_lower or "pest" in message_lower:
            return "Contact local agriculture department immediately. Use certified pesticides and follow integrated pest management practices."
        elif "low" in message_lower and ("production" in message_lower or "yield" in message_lower):
            return "Test soil fertility, use balanced fertilizers, and consider high-yield varieties suitable for your region."
        elif "loan" in message_lower or "money" in message_lower:
            return "Maintain proper farm records and bank transactions. KCC offers the lowest interest rates for farmers."
        else:
            return ""
    
    def _get_practical_advice_hindi(self, message, intent):
        """Get practical farming advice in Hindi"""
        message_lower = message.lower()
        
        if "water" in message_lower or "irrigation" in message_lower:
            return "बाढ़ वाले सिंचाई की तुलना में ड्रिप सिंचाई पर विचार करें, इससे 30-50% पानी बचता है। मल्चिंग भी मिट्टी की नमी बनाए रखने में मदद करता है।"
        elif "disease" in message_lower or "pest" in message_lower:
            return "तुरंत स्थानीय कृषि विभाग से संपर्क करें। प्रमाणित कीटनाशकों का उपयोग करें और समग्र कीट प्रबंधन अपनाएं।"
        elif "low" in message_lower and ("production" in message_lower or "yield" in message_lower):
            return "मिट्टी की उर्वरा की जांच करें, संतुलित उर्वरकों का उपयोग करें, और अपने क्षेत्र के अनुकूल उच्च उपजाऊ विविधियों पर विचार करें।"
        elif "loan" in message_lower or "money" in message_lower:
            return "उचित खेत रिकॉर्ड और बैंक लेनदेन रखें। किसान क्रेडिट कार्ड किसानों के लिए सबसे कम ब्याज दर प्रदान करता है।"
        else:
            return ""
    
    def _get_practical_advice_marathi(self, message, intent):
        """Get practical farming advice in Marathi"""
        message_lower = message.lower()
        
        if "water" in message_lower or "irrigation" in message_lower:
            return "पाणी शेतण्याच्या तुलनात ड्रिप सिंचाई विचारा, यामुळे ३०-५०% पाणी वाचते. मल्चिंग देखील जमिनीचे ओले टिकवून ठेवते."
        elif "disease" in message_lower or "pest" in message_lower:
            return "तात्काळ स्थानिक शेती विभागाशी संपर्क साधा. प्रमाणित कीटकाळकांचा वापर करा आणि एकत्रित कीट व्यवस्थापन वापरा."
        elif "low" in message_lower and ("production" in message_lower or "yield" in message_lower):
            return "जमिनीची उत्पादकता तपासा, समतोल सारे वापरा आणि तुमच्या प्रदेशासाठी योग्य उच्च उत्पादन जातीं विचारा."
        elif "loan" in message_lower or "money" in message_lower:
            return "योग्य शेती नोंदणी आणि बँक व्यवहार ठेवा. किसान क्रेडिट कार्ड शेतकऱ्यांसाठी सर्वात कमी व्याज दर देते."
        else:
            return ""
