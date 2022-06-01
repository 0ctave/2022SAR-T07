import enum
import string
import matplotlib.pyplot as plt
from IPython.display import clear_output

class LineGraph :

    data_t:list
    data_x:list

    x_legend:str
    y_legend:str
    title:str

    def __init__(self,title:str="sample title",x_legend:str="",y_legend:str="") -> None:
        self.data_t = []
        self.data_x = []

        self.title = title
        self.x_legend = x_legend
        self.y_legend = y_legend

        self.refreshDisplay()

    def addPoint(self,t:float,x:float,refresh:bool=True) -> None:
        """Add a point into the graph display
        t : time
        x : value at time t
        refresh : display the refreshed graph display if True, else nothing changes
        """
        self.data_t.append(t)
        self.data_x.append(x)
        if refresh :
            self.refreshDisplay()


    def refreshDisplay(self) :
        """Refresh the graph display"""
        clear_output(wait=True)
        plt.plot(self.data_t, self.data_x)
        self._addLegend()
        plt.show()

    def _addLegend(self):
        """Automatically add a legend"""
        plt.xlabel(self.x_legend)
        plt.ylabel(self.y_legend)
        plt.title(self.title)
        plt.legend()

class MultipleLineGraph :

    data_t = []
    data_multiple:list
    dimension:int

    x_legend:str
    y_legend:str
    title:str
    lines_title:list[str]

    def __init__(self,lines_title:list[str],title:str="sample title",x_legend:str="",y_legend:str="") -> None:
        """Initialise a LineGraph with lines"""

        self.dimension = len(lines_title)

        self.data_multiple = [[] for _ in range(self.dimension)]
        self.data_t = []

        self.title = title
        self.x_legend = x_legend
        self.y_legend = y_legend

        self.lines_title = lines_title

        self.refreshDisplay()

    def addPoint(self,t:float,X:list,refresh:bool=True) :
        """Add a point into the graph display
        t : time
        X : values of differents lines at time t, in the same order
        refresh : display the refreshed graph display if True, else nothing changes
        """
        self.data_t.append(t)
        for i,xi in enumerate(self.data_multiple) :
            xi.append(X[i])
        
        if refresh :
            self.refreshDisplay()


    def refreshDisplay(self) :
        clear_output(wait=True)
        
        for i,xi in enumerate(self.data_multiple) :
            plt.plot(self.data_t,xi,label=self.lines_title[i])

        self._addLegend()
        plt.show()

    def _addLegend(self):
        plt.xlabel(self.x_legend)
        plt.ylabel(self.y_legend)
        plt.title(self.title)
        plt.legend()

if __name__ == "__main__" :
    test = MultipleLineGraph(['item1','item2'],"items")
    test.addPoint(t=1,X=[2,3])
    test.addPoint(t=2,X=[6,7])