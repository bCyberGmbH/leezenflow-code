# This animation was created during the Münsterhack 2021.
# Idea: You will make it in time when the bike is inside the green window while your passing the LED

import time
from rgbmatrix import graphics
from PIL import Image, ImageDraw

from leezenflow_base import LeezenflowBase
from shared_state import SharedState

class AnimationMSHACK(LeezenflowBase):
    def __init__(self, command_line_args):
        super(AnimationMSHACK, self).__init__(command_line_args)
       
    def run(self,_,run_event):
        print("MSHACK2021")

        w = 32
        h = 96
        upper_end = 10
        lower_end = h - 28
        meter_per_pixel = (lower_end - upper_end) / 120.0
        speed_of_bike = 5.555 # meter per second, this is a guess of an average cyclist's speed

        ### Start the loop ###
        while(run_event.is_set()):
            remaining_time = max(0, SharedState.shared_data["change_timestamp"] - SharedState.shared_data["current_timestamp"])

            color_map = {
                "red": "#a52019",
                "green": "#008754",
                "red-yellow": "#ff0",
                "yellow": "#ff0"
            }
            color_unknown = '#00f' # blue

            image = Image.new(mode="RGB", size=(w, h), color='black')
            draw = ImageDraw.Draw(image)
            
            def draw_phase_bar(phase_type, length_in_seconds, position):
                length_in_meter = length_in_seconds * speed_of_bike
                length_in_pixel = round(length_in_meter * meter_per_pixel)
                draw.rectangle([(0, position), (w, position + length_in_pixel)], fill=color_map.get(phase_type, color_unknown), outline=None)
                return position + length_in_pixel
           
            draw_position = upper_end
            draw_phase = { "type": SharedState.shared_data["current_phase"], "length": remaining_time }
            for i in range(5):
                draw_position = draw_phase_bar(draw_phase["type"], draw_phase["length"], draw_position)
                draw_phase = get_next_phase(draw_phase)

            # draw.rectangle([(0, lower_end), (w, h)], fill="yellow", outline=None)

            overlay = Image.open("animations/mshack_overlay.png")
            overlay_draw = ImageDraw.Draw(overlay)
            if SharedState.shared_data["current_phase"] == "red" or SharedState.shared_data["current_phase"] == "red-yellow":
                overlay_draw.rectangle([
                    (round(w / 2) - 2, 4),
                    (round(w / 2) + 1, 5)
                ], fill="red", outline=None)
                overlay_draw.rectangle([
                    (round(w / 2) - 1, 3),
                    (round(w / 2) + 0, 6)
                ], fill="red", outline=None)
            if SharedState.shared_data["current_phase"] == "yellow" or SharedState.shared_data["current_phase"] == "red-yellow":
                overlay_draw.rectangle([
                    (round(w / 2) - 2, 9),
                    (round(w / 2) + 1, 10)
                ], fill="yellow", outline=None)
                overlay_draw.rectangle([
                    (round(w / 2) - 1, 8),
                    (round(w / 2) + 0, 11)
                ], fill="yellow", outline=None)
            if SharedState.shared_data["current_phase"] == "green":
                overlay_draw.rectangle([
                    (round(w / 2) - 2, 14),
                    (round(w / 2) + 1, 15)
                ], fill="green", outline=None)
                overlay_draw.rectangle([
                    (round(w / 2) - 1, 13),
                    (round(w / 2) + 0, 16)
                ], fill="green", outline=None)
            
            image.paste(overlay, (0, 0), overlay)

            self.matrix.SetImage(image.rotate(270, expand=True).convert('RGB'))
            time.sleep(0.2)
            
        
def get_next_phase(current_phase):
    if current_phase["type"] == "red":
        return {"type": "red-yellow", "length": 2}
    if current_phase["type"] == "red-yellow":
        return {"type": "green", "length": 18}
    if current_phase["type"] == "green":
        return {"type": "yellow", "length": 2}
    if current_phase["type"] == "yellow":
        return {"type": "red", "length": 38}
    return {"type": "unknown", "length": 30}


