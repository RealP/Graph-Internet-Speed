"""
Create an html file for viewing SpeedTester data.

Choose what you want too see.
    ie : download, uploads or both (more options to follow)
Allows for filtering on any attribute in json data
    ie : ssid, Provider or ip_address
Requirements
    plotly
    matplotlib
"""
__author__ = "Paul Pfeffer"

import re
import datetime
import itertools
import plotly

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def filter_data(data, filter_key, filter_value):
    """
    Filter out specific key value pairs from data collected.

    @param filter_key all keys are available for filtering however
     the only ones that make sense are : (ssid, Provider)
    """
    new_data = {}
    for date, data in data.iteritems():
        keep_data = False
        for key, val in data.iteritems():
            if key.strip() == filter_key and val.strip() == filter_value:
                keep_data = True
        if keep_data:
            new_data[date] = data
    return new_data


def parse_data(self, parsedays=True):
    """
    Parse speedtester data into local variables.

    @param self instance of either DrawWithPlotly or DrawWithPyPlot
    @param parsedays whether to parse days or not (default:True)
                     if False all days will be treated as the same
    """
    self.timestamps = []
    self.upload_speeds = []
    self.download_speeds = []
    self.ping_speeds = []
    self.ssid_names = []
    self.all_info = []
    self.uids = []
    for key, val in sorted(self.speeddata.iteritems()):
        d = re.search(self.datetime_regex, key)
        self.timestamps.append(datetime.datetime(
            year=int(d.group(1)),
            month=int(d.group(2)),
            day=int(d.group(3)),
            hour=int(d.group(4)),
            minute=int(d.group(5)),
            second=int(d.group(6)))
        )
        self.all_info.append(val["all_info"])
        self.upload_speeds.append(float(re.search(self.number, val["upload"]).group(1)))
        self.download_speeds.append(float(re.search(self.number, val["download"]).group(1)))
        self.ping_speeds.append(float(re.search(self.number, val["ping"]).group(1)))
        self.ssid_names.append(val["ssid"])
    if not parsedays:
        self.timestamps = [item.replace(year=2000, month=1, day=1) for item in self.timestamps]


class DrawWithPyPlot(object):
    """Draw SpeedTester data with matplotlib."""

    def __init__(self, speeddata):
        """
        Initialize DrawWithPyPlot.

        @param speeddata SpeedTester results.
        """
        super(DrawWithPyPlot, self).__init__()
        self.speeddata = speeddata
        self.datetime_regex = r"(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)"
        self.number = r"(\d.+)(M|m)"
        self.mpl_fig_obj, self.ax = plt.subplots(1)
        # self.mpl_fig_obj = plt.figure()

        self.closest_x_val = None
        self.closest_x_idx = None
        self.closest_y_val = None
        self.closest_y_idx = None
        self.extra_annotation = None
        # Available modes hover_view, inspect_view
        self.cur_mode = "hover_view"

    def set_data(self, data):
        """Set the data that will be graphed.

        @param data a dictionary element that represents the generic data form:
                    ie) {
                            "name":"Upload",
                            "unit":"Mbit/s",
                            "data":self.download_speeds
                        }
        """
        self.data = data
        if "download" in data["name"].lower():
            self.aux_data1 = {
                "name": "Upload",
                "unit": "Mbit/s",
                "data": self.upload_speeds
            }
            self.aux_data2 = {
                "name": "Ping",
                "unit": "ms",
                "data": self.ping_speeds
            }
        elif "upload" in data["name"].lower():
            self.aux_data1 = {
                "name": "Download",
                "unit": "Mbit/s",
                "data": self.download_speeds
            }
            self.aux_data2 = {
                "name": "Ping",
                "unit": "ms",
                "data": self.ping_speeds
            }
        else:
            self.aux_data1 = {
                "name": "Download",
                "unit": "Mbit/s",
                "data": self.download_speeds
            }
            self.aux_data2 = {
                "name": "Upload",
                "unit": "Mbit/s",
                "data": self.upload_speeds
            }

    def draw_data(self):
        """Create and show the plot."""

        # Create the plot
        plt.plot(self.timestamps, self.data["data"], label=self.data["name"], picker=True)
        # plt.scatter(self.timestamps, self.data, label="Download Speed", marker='o', picker=True)
        plt.title("Internet Speeds")
        plt.grid(True)

        # Turn on interactive mode
        # plt.ion()

        # Format X axis DATE
        plt.xlabel("Datetime")
        self.mpl_fig_obj.autofmt_xdate()

        # Format X axis SPEED
        plt.ylabel("Mbit/s")

        # Extra annotations
        self.annotate_max()
        self.annotate_min()
        self.annotate_median()
        self.annotate_mean()
        self.annotate_running_average()

        # Make a legend
        plt.legend(loc='upper right')

        # Set up event handlers
        self.mpl_fig_obj.canvas.mpl_connect('pick_event', self.on_pick_event)
        self.mpl_fig_obj.canvas.mpl_connect('button_release_event', self.on_mouse_up)
        # self.mpl_fig_obj.canvas.mpl_connect('button_press_event', self.on_mouse_up)
        self.mpl_fig_obj.canvas.mpl_connect('motion_notify_event', self.on_hover)
        plt.show()

    def annotate_max(self):
        """Add annotation for the max point in the plot."""
        index, val = self.get_max_index_and_value(self.data["data"])
        plt.annotate(
            "Max: {ts}\n{primary_name}: {val} {primary_unit}\n{second_name}: {val2} {secondary_unit}\n{third_name}: {val3} {third_unit}".format(
                ts=self.timestamps[index],
                primary_name=self.data["name"],
                val=self.data["data"][index],
                primary_unit=self.data["unit"],
                second_name=self.aux_data1["name"],
                val2=self.aux_data1["data"][index],
                secondary_unit=self.aux_data1["unit"],
                third_name=self.aux_data2["name"],
                val3=self.aux_data2["data"][index],
                third_unit=self.aux_data2["unit"]
            ),
            xy=(self.timestamps[index], self.data["data"][index]), xytext=(-20, 20),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
            arrowprops=dict(arrowstyle='fancy', connectionstyle='arc3,rad=0'))

    def annotate_min(self):
        """Add annotation for the min point in the plot."""
        index, val = self.get_min_index_and_value(self.data["data"])
        return plt.annotate(
            "Min: {ts}\n{primary_name}: {val} {primary_unit}\n{second_name}: {val2} {secondary_unit}\n{third_name}: {val3} {third_unit}".format(
                ts=self.timestamps[index],
                primary_name=self.data["name"],
                val=self.data["data"][index],
                primary_unit=self.data["unit"],
                second_name=self.aux_data1["name"],
                val2=self.aux_data1["data"][index],
                secondary_unit=self.aux_data1["unit"],
                third_name=self.aux_data2["name"],
                val3=self.aux_data2["data"][index],
                third_unit=self.aux_data2["unit"]
            ),
            xy=(self.timestamps[index], self.data["data"][index]), xytext=(-20, 20),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
            arrowprops=dict(arrowstyle='fancy', connectionstyle='arc3,rad=0'))

    def annotate_mean(self):
        """Add annotation for the mean."""
        mean = np.mean(self.data["data"])
        y_mean = [mean for _ in self.timestamps]
        plt.plot(self.timestamps, y_mean, label="{0} Mean".format(self.data["name"]), linestyle='--')

    def annotate_running_average(self):
        """Add annotation for the running average."""
        # Calculate what running average
        avg = self.data["data"][0]
        r_avg = [avg]
        for i in self.data["data"][1:]:
            avg = (avg + i) / 2
            r_avg.append(avg)
        plt.plot(self.timestamps, r_avg, label="Running Avg", linestyle='--')

    def annotate_median(self):
        """Add annotation for the median point in the plot."""
        index, val = self.get_median_index_and_value(self.data["data"])
        return plt.annotate(
            "Median: {ts}\n{primary_name}: {val} {primary_unit}\n{second_name}: {val2} {secondary_unit}\n{third_name}: {val3} {third_unit}".format(
                ts=self.timestamps[index],
                primary_name=self.data["name"],
                val=self.data["data"][index],
                primary_unit=self.data["unit"],
                second_name=self.aux_data1["name"],
                val2=self.aux_data1["data"][index],
                secondary_unit=self.aux_data1["unit"],
                third_name=self.aux_data2["name"],
                val3=self.aux_data2["data"][index],
                third_unit=self.aux_data2["unit"]
            ),
            xy=(self.timestamps[index], self.data["data"][index]), xytext=(-20, 20),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
            arrowprops=dict(arrowstyle='fancy', connectionstyle='arc3,rad=0'))

    def annotate_hover_point(self, idx):
        """Highligh a point."""
        # print (self.cur_mode)
        if self.extra_annotation and self.cur_mode == "hover_view":
            self.extra_annotation.remove()
        new_annotation = plt.annotate(
            "{0} {1}\n{2}".format(self.data["data"][idx], self.data["unit"], self.timestamps[idx]),
            xy=(self.timestamps[idx], self.data["data"][idx]), xytext=(-20, -20),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.9),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        self.mpl_fig_obj.canvas.draw()
        return new_annotation

    def annotate_click_point(self, idx):
        """Highligh a point."""
        if self.extra_annotation:
            self.extra_annotation.remove()
            self.extra_annotation = None
        new_annotation = plt.annotate(
            "{0}".format(re.sub(r'(\.{3,})', r"\1\n", self.all_info[idx]).replace("\r\n", "\n")),
            xy=(self.timestamps[idx], self.data["data"][idx]), xytext=(-20, -20),
            textcoords='offset points', ha='left', va='bottom', family="monospace",
            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.9),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        self.mpl_fig_obj.canvas.draw()
        return new_annotation

    def on_pick_event(self, event):
        """
        Event handler for click event.

        @param event event that occurred
        """
        self.cur_mode = "inspect_view"
        ind = event.ind[0]
        # print 'onpick3 scatter:', ind, np.take(self.timestamps, ind), np.take(self.data["data"], ind)
        self.extra_annotation = self.annotate_click_point(ind)

    def on_hover(self, event):
        """
        Event handler for mouse move event.

        @param event event that occurred
        """
        # get the x and y pixel coords
        if event.inaxes:
            x_idx, x_val = self.get_index_and_value_of_nearest_date(self.timestamps, mdates.num2date(event.xdata))
            y_idx, y_val = self.get_index_and_value_of_nearest(self.data["data"], event.ydata)

            if x_idx != self.closest_x_idx:
                self.extra_annotation = self.annotate_hover_point(x_idx)
                self.closest_x_idx = x_idx
            if y_idx != self.closest_y_idx:
                self.closest_y_idx = y_idx

    def on_mouse_up(self, event):
        """
        Event handler for mouse click is released.

        @param event event that occurred
        """
        # get the x and y pixel coords
        # print ("on_mouse_up")
        if self.cur_mode == "inspect_view":
            self.cur_mode = "hover_view"
            self.extra_annotation.remove()
            self.extra_annotation = None

    def get_index_and_value_of_nearest(self, array, value):
        """
        Get the index and value of item with closest value in array.

        @param array array to get element with closest value
        @param value the value to search array for
        """

        idx = (np.abs(array - value)).argmin()
        return idx, array[idx]

    def get_index_and_value_of_nearest_date(self, items, pivot):
        """
        Get the index and value from datetime with the closest time.

        @param items array of datetime objects
        @param pivot the datetime value to search array for
        """
        nearest_val = min(items, key=lambda x: abs(x - datetime.datetime.replace(pivot, tzinfo=None)))
        nearest_idx = items.index(nearest_val)
        return nearest_idx, items[nearest_idx]

    @staticmethod
    def get_max_index_and_value(l):
        """
        Get the index and value of the highest element in list.

        @param l the list from which you want the highest element
        """
        max_val = max(l)
        max_idx = l.index(max_val)
        return max_idx, max_val

    @staticmethod
    def get_min_index_and_value(l):
        """
        Get the index and value of the lowest element in list.

        @param l the list from which you want the lowest element
        """
        min_val = min(l)
        min_idx = l.index(min_val)
        return min_idx, min_val

    @staticmethod
    def get_median_index_and_value(l):
        """
        Get the index and value of the median element in list.

        @param l the list from which you want the median
        """
        if len(l) % 2 == 0:
            l = l[1:]
        median_val = np.median(l)
        median_idx = l.index(median_val)
        return median_idx, median_val


class DrawWithPlotly(object):
    """Draw SpeedTester data with plot.ly."""

    def __init__(self, speeddata):
        """Initialize main data and some regexes."""
        super(DrawWithPlotly, self).__init__()
        self.speeddata = speeddata
        self.datetime_regex = r"(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)"
        self.number = r"(\d.+)(M|m)"

    def get_template_trace(self, graph):
        """
        Initialize a default ploty graph.

        @retval Returns template trace.
        """
        upload_text = ["Upload : %s Mbit/s" % (str(i)) for i in self.upload_speeds]
        download_text = ["Download : %s Mbit/s" % (str(i))for i in self.download_speeds]
        ping_text = ["Ping : %s ms" % (str(i)) for i in self.ping_speeds]
        ssid_text = ["SSID : %s" % (str(i)) for i in self.ssid_names]
        display_text = ["%s<br>%s<br>%s<br>%s" % (a, b, c, d)
                        for a, b, c, d in itertools.izip(ssid_text, upload_text, download_text, ping_text)]
        return plotly.graph_objs.Scatter(
            x=self.timestamps,
            text=display_text,
            mode='markers',
            line=dict(
                shape='spline'
            ),
            marker=plotly.graph_objs.Marker(
                size=5,
                line=plotly.graph_objs.Line(width=1.0), opacity=0.5
            )
        )

    def set_data(self, graph):
        """
        Initialize data by with the trace types provided in graph.

        @param graph A string or list of strings containing the data types to graph
                        Current options : download, upload
        """
        data = []
        if ("download" in graph):
            y_axis = self.download_speeds
            y_name = "Download"
            download_trace = self.get_template_trace(graph)
            setattr(download_trace, "y", y_axis)
            setattr(download_trace, "name", y_name)
            data.append(download_trace)
            # setattr(download_trace, "uid", self.download_ids)
        if ("upload" in graph):
            y_axis = self.upload_speeds
            y_name = "Upload"
            upload_trace = self.get_template_trace(graph)
            setattr(upload_trace, "y", y_axis)
            setattr(upload_trace, "name", y_name)
            data.append(upload_trace)
        self.data = data

    def setup_layout(self):
        """Hard coded layout values exist here. Try moving to json."""
        self.layout = plotly.graph_objs.Layout(
            title="Internet Speeds",
            xaxis=dict(
                title='Date Time',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=22,
                    color='#000000'
                )
            ),
            yaxis=dict(
                title='Mbit/s',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=22,
                    color='#000000'
                )
            ),
            legend=dict(
                # x=0,
                # y=1,
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=16,
                    color='#000'
                ),
                bgcolor='#E2E2E2',
                bordercolor='#FFFFFF',
                borderwidth=2
            )
        )

    def draw_data(self):
        """Call to set up layout and plotly plot to make html page."""
        self.setup_layout()
        fig = plotly.graph_objs.Figure(data=self.data, layout=self.layout)
        plotly.offline.plot(fig, filename='speedresults.html')


def main():
    """Example of how to use the classes."""

    # The data for the classes is the same
    import json
    results_file = "speedresults.json"
    with open(results_file) as f:
        results = json.load(f)

    # # Using the DrawWithPlotly Class
    # d_speed = DrawWithPlotly(results)
    # # d_speed.speeddata = filter_data(d_speed.speeddata, "ssid", "ssid_name")
    # parse_data(d_speed, parsedays=True)
    # d_speed.set_data(["download"])  # You can also specify just upload or download
    # d_speed.draw_data()  # Graph it!

    # Using the DrawWithPyPlot Class
    d_speed = DrawWithPyPlot(results)
    # d_speed.speeddata = filter_data(d_speed.speeddata, "ssid", "ssid_name")
    parse_data(d_speed, parsedays=True)
    # Here you can set up what data you want to graph
    d_speed.set_data({"name": "Download", "unit": "Mbit/s", "data": d_speed.download_speeds})
    # d_speed.set_data({"name": "Upload", "unit": "Mbit/s", "data": d_speed.upload_speeds})
    # d_speed.set_data({"name": "Ping", "unit": "ms", "data": d_speed.ping_speeds})
    d_speed.draw_data()  # Graph it!


if __name__ == '__main__':
    main()
