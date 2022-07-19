from message_interpreter import Interpreter
import time

class Simulation():    

    # Tests that replays recorded phases
    def mqtt_client_simulation(leezenflow_object,_,run_event):
        import io
        with io.open('sample_messages/spat.log','r',encoding='utf8') as f:
            text = f.read()
        spat_xml = text.split("/rsu/forward/spat ")
        spat_xml = spat_xml[1:] #Remove leading whitespace

        interpreter = Interpreter()

        for spatem_xml in spat_xml: 
            time.sleep(0.1) # Test dataset has 10 updates per second -> 0.1
            leezenflow_object.shared_data = interpreter.interpret_message(spatem_xml)
            print("Simulated: ",leezenflow_object.shared_data,flush=True)
            if not run_event.is_set():
                break    

    # Tests that replays recorded phases
    def mqtt_client_simulation_dataframe(leezenflow_object,_,run_event):
        import pickle
        import pandas as pd
        from message_modifier import ModifierHoerstertor

        df = pickle.load( open( "sample_messages/log8.p", "rb" ) )
        df = df[df.signalGroup == "33"]
        df = df.drop_duplicates(subset='xml_file', keep='first')
        df['time'] = pd.to_datetime(df['time'])

        modify = ModifierHoerstertor().smooth

        for i in range(len(df)):
            time.sleep(0.1) # Test dataset has 10 updates per second -> 0.1
            row = df.iloc[i,:]

            current_time = time.monotonic()
            shared_data = {
                "current_phase" : row.current_phase,
                "current_timestamp" : current_time,
                "change_timestamp" : current_time + int(row.remaining_time),
                "hash" : row.current_phase + str(row.likelyTime)
            }

            #leezenflow_object.shared_data = shared_data
            leezenflow_object.shared_data = modify(shared_data)

            print("Simulated: ",leezenflow_object.shared_data,flush=True)

            if not run_event.is_set():
                break 

    # Tests a continous phase switch with fixed time
    def phase_switch_simulation(leezenflow_object,target,run_event):
        while run_event.is_set():
            for i in range(0,target):
                leezenflow_object.shared_data = {
                    "current_phase" : "green",
                    "current_timestamp": i,
                    "change_timestamp" : target,
                    "hash" : "A"
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)  
                if not run_event.is_set():
                    break      
            for i in range(0,target):
                leezenflow_object.shared_data = {
                    "current_phase" : "red",
                    "current_timestamp": i,
                    "change_timestamp" : target,
                    "hash" : "B"
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)
                if not run_event.is_set():
                    break 

    # Tests a continous phase switch with all four phases red->red-yellow->green->yellow->...
    def phase_switch_simulation_4_phases(leezenflow_object,target,run_event):
        mini_phase = 1
        while run_event.is_set():
            for i in range(0,target):
                leezenflow_object.shared_data = {
                    "current_phase" : "red",
                    "current_timestamp": i,
                    "change_timestamp" : target,
                    "hash" : "R"
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)  
                if not run_event.is_set():
                    break      
            for i in range(0,mini_phase):
                leezenflow_object.shared_data = {
                    "current_phase" : "red-yellow",
                    "current_timestamp": i,
                    "change_timestamp" : mini_phase,
                    "hash" : "RY"
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)  
                if not run_event.is_set():
                    break         
            for i in range(0,target):
                leezenflow_object.shared_data = {
                    "current_phase" : "green",
                    "current_timestamp": i,
                    "change_timestamp" : target,
                    "hash" : "G"
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)
                if not run_event.is_set():
                    break
            for i in range(0,mini_phase):
                leezenflow_object.shared_data = {
                    "current_phase" : "yellow",
                    "current_timestamp": i,
                    "change_timestamp" : mini_phase,
                    "hash" : "Y"
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)  
                if not run_event.is_set():
                    break              

    # Tests a jumping non-steady prediction; e.g. from predicted 20 seconds, to 40 seconds, back to 10.
    def phase_update_simulation(leezenflow_object,color,run_event):
        timestamp = 0
        for i in range(0,5):
            timestamp += 1
            leezenflow_object.shared_data = {
                "current_phase" : color,
                "current_timestamp": timestamp,
                "change_timestamp" : 15,
                "hash" : "A"
                }
            print(leezenflow_object.shared_data)
            time.sleep(1)
            if not run_event.is_set():
                break
        for i in range(0,10):
            timestamp += 1
            leezenflow_object.shared_data = {
                "current_phase" : color,
                "current_timestamp": timestamp,
                "change_timestamp" : 50,
                "hash" : "B" 
                }
            time.sleep(1)
            print(leezenflow_object.shared_data)
            if not run_event.is_set():
                break                       
        for i in range(0,10):
            timestamp += 1
            leezenflow_object.shared_data = {
                "current_phase" : color,
                "current_timestamp": timestamp,
                "change_timestamp" : 21,
                "hash" : "C" 
                }
            time.sleep(1)
            print(leezenflow_object.shared_data)
            if not run_event.is_set():
                break

    # Tests high frequency updates
    def phase_fast_simulation(leezenflow_object,color,run_event):
        frequency = 10
        for i in range(0,200):
            leezenflow_object.shared_data = {
                "current_phase" : color,
                "current_timestamp": int(i/frequency),
                "change_timestamp" : 20,
                "hash" : "A" 
                }
            time.sleep(1/frequency)
            print(leezenflow_object.shared_data)
            if not run_event.is_set():
                break        

    # Tests stale prediction
    def stale_prediction(leezenflow_object,_,run_event):
        while run_event.is_set():
            for i in range(3):
                leezenflow_object.shared_data = {
                    "current_phase" : "red",
                    "current_timestamp": i,
                    "change_timestamp" : 3,
                    "hash" : "A" 
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)  
                if not run_event.is_set():
                    break      
            for i in range(10):
                leezenflow_object.shared_data = {
                    "current_phase" : "red",
                    "current_timestamp": 6.0 + i,
                    "change_timestamp" : 6.0 + i,
                    "hash" : "A" 
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)
                if not run_event.is_set():
                    break  
            for i in range(10):
                leezenflow_object.shared_data = {
                    "current_phase" : "green",
                    "current_timestamp": i,
                    "change_timestamp" : 10,
                    "hash" : "B" 
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)
                if not run_event.is_set():
                    break  
