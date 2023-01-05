import abc

class AbstractLeezenflowDisplay(abc.ABC):
    
    from shared_state import SharedState

    @abc.abstractmethod
    def GetDisplayType(self):
        pass

    @abc.abstractmethod
    def setPixel(self, row, pixel, r, g, b):
        pass

    @abc.abstractmethod
    def Fill(self, r, g, b):
        pass
    
    @abc.abstractmethod
    def setRow(self, row_nr):
        pass
            
    @abc.abstractmethod
    def draw_rectangle(self, y1, y2, r, g, b):
        pass
            
    @abc.abstractmethod
    def draw_rectangle_shade(self, y1, y2, r, g, b):
        pass
            
    @abc.abstractmethod
    def draw_black_trend_rectangle(self, y1, y2, r, g, b):
        pass
            
    @abc.abstractmethod
    def draw_bike(self, r, g, b, y_position, axis_x_left, moving = False):
        pass