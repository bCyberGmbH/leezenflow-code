from leezenflow_base import LeezenflowBase
from rgbmatrix import graphics
import time
from shared_state import SharedState

class AnimationSignal(LeezenflowBase):
    def __init__(self, command_line_args):
        super(AnimationSignal, self).__init__(command_line_args)

        self.MATRIX_HEIGHT = 96
        self.MATRIX_WIDTH = 32                
        SharedState.shared_data = SharedState.shared_data
       
    def run(self,_,run_event):

        canvas = self.matrix

        def draw_rectangle(x0,y0,x1,y1,r,g,b):
            for row in range(y0,y1):
                graphics.DrawLine(canvas, row, x0, row, x1, graphics.Color(r,g,b))

        timer = time.monotonic()
        time_window = 10
        update_array = []
        current_hash = 0

        while(run_event.is_set()):
            print(SharedState.shared_data)
            if current_hash != (current_hash := SharedState.shared_data["hash"]):
                update_array.append(time.monotonic())
            update_array = [t for t in update_array if (t + time_window) > time.monotonic()]
            messages_in_time_window = len(update_array)
            print(messages_in_time_window)

            canvas.Fill(0,0,0)
            draw_rectangle(x0=0,y0=0, x1=self.MATRIX_WIDTH, y1=min(messages_in_time_window, self.MATRIX_HEIGHT), r=45,g=114,b=135)
            time.sleep(0.2)
