class SharedState:
    # Initialize status dictionary that is shared by the interpretation and animation logic
    shared_data = {
                "current_phase" : "awaiting_message",
                "current_timestamp" : 0,
                "change_timestamp" : 15,
                "hash" : 0 
            }
    interpreter = None