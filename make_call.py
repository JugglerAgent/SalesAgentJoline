from services.twilio_service import TwilioService

def main():
    try:
        ts = TwilioService()
        call = ts.make_outbound_call(
            "+27834598995",
            "Hi Schalk, I am Joline, your AI Sales Agent"
        )
        print(f"Call initiated with SID: {call.sid}")
    except Exception as e:
        print(f"Error making call: {str(e)}")

if __name__ == "__main__":
    main()