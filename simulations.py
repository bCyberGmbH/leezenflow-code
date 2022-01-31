from mqtt_message_interpreter import Interpreter
import time

class Simulation():    

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

    def mqtt_client_simulation_dataframe(leezenflow_object,_,run_event):
        import pickle
        import pandas as pd
        from smoother import HoersterTorSmoother

        df = pickle.load( open( "sample_messages/log8.p", "rb" ) )
        df = df[df.signalGroup == "33"]
        df = df.drop_duplicates(subset='xml_file', keep='first')
        df['time'] = pd.to_datetime(df['time'])

        smoother = HoersterTorSmoother()

        for i in range(len(df)):
            time.sleep(0.1) # Test dataset has 10 updates per second -> 0.1
            row = df.iloc[i,:]
            
            shared_data = {
                "current_phase" : row.current_phase,
                "remaining_time" : row.remaining_time,
                "prediction_absolute" : row.likelyTime,
            }

            #leezenflow_object.shared_data = shared_data
            leezenflow_object.shared_data = smoother.smooth(shared_data)

            print("Simulated: ",leezenflow_object.shared_data,flush=True)

            if not run_event.is_set():
                break 

    def phase_switch_simulation(leezenflow_object,speed,run_event):
        while run_event.is_set():
            for i in range(speed,0,-1):
                leezenflow_object.shared_data = {
                    "current_phase" : "green",
                    "remaining_time" : i
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)  
                if not run_event.is_set():
                    break      
            for i in range(speed,0,-1):
                leezenflow_object.shared_data = {
                    "current_phase" : "red",
                    "remaining_time" : i
                    }
                time.sleep(1)
                print(leezenflow_object.shared_data)
                if not run_event.is_set():
                    break 

    def phase_update_simulation(leezenflow_object,color,run_event):
        for i in range(5,0,-1):
            leezenflow_object.shared_data = {
                "current_phase" : color,
                "remaining_time" : i+15
                }
            print(leezenflow_object.shared_data)
            time.sleep(1)
            if not run_event.is_set():
                break
        for i in range(10,0,-1):
            leezenflow_object.shared_data = {
                "current_phase" : color,
                "remaining_time" : i+30
                }
            time.sleep(1)
            print(leezenflow_object.shared_data)
            if not run_event.is_set():
                break                       
        for i in range(10,0,-1):
            leezenflow_object.shared_data = {
                "current_phase" : color,
                "remaining_time" : i
                }
            time.sleep(1)
            print(leezenflow_object.shared_data)
            if not run_event.is_set():
                break

    def phase_fast_simulation(leezenflow_object,color,run_event):
        for i in range(100,0,-1):
            leezenflow_object.shared_data = {
                "current_phase" : color,
                "remaining_time" : int(i/5)
                }
            time.sleep(0.2)
            print(leezenflow_object.shared_data)
            if not run_event.is_set():
                break        
