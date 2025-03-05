class AgentConfig:
    # Agent Identity
    AGENT_NAME = "Joline"
    AGENT_WORKPLACE = "Zeevenwacht Restaurant"
    
    # Conversation Parameters
    MAX_RESPONSE_WORDS = 70  # Maximum words per response to keep conversations concise
    
    # Call Handling Rules
    CALL_RULES = {
        "think_out_loud": False,  # Never verbalize thoughts during calls
        "audio_only": True,      # Only use audio responses during calls
        "end_call_message": ""   # No verbal end call message
    }
    
    # Information Handling
    UNKNOWN_INFO_RESPONSE = "I apologize, I don't have that information. I can reach out to the team to get those details for you."
    
    @classmethod
    def get_identity(cls):
        return {
            "name": cls.AGENT_NAME,
            "workplace": cls.AGENT_WORKPLACE
        }
    
    @classmethod
    def validate_response_length(cls, response):
        """Check if response is within the word limit"""
        words = response.split()
        return len(words) <= cls.MAX_RESPONSE_WORDS