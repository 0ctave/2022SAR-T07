import string
import matplotlib.pyplot as plt
from IPython.display import clear_output

class LineGraph :

    data_t:list
    data_x:list

    x_legend:str
    y_legend:str
    title:str

    def __init__(self,title="sample title",x_legend="",y_legend="") -> None:
        self.data_t = []
        self.data_x = []

        self.title = title
        self.x_legend = x_legend
        self.y_legend = y_legend

        self.refreshDisplay()

    def addPoint(self,t,x,refresh=true) :
        self.data_t.append(t)
        self.data_x.append(x)
        if refresh :
            self.refreshDisplay()


    def refreshDisplay(self) :
        clear_output(wait=True) # Clear / remove whatever was already plotted before
        plt.plot(self.data_t, self.data_x) # Re-plot the data with the new added values in the list
        self._addLegend()
        plt.show() # Make sure to display the new plot, to make it visible

    def _addLegend(self):
        plt.xlabel(self.x_legend)
        plt.ylabel(self.y_legend)
        plt.title(self.title)

if __name__ == "__main__" :
    test = LineGraph("hello")
    test.addPoint(1,4)
    test.addPoint(2,5)