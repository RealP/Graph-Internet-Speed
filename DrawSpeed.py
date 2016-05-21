"""
Create an html file for viewing SpeedTester data.

Choose what you want too see.
    ie : download, uploads or both (more options to follow)
Allows for filtering on any attribute in json data
    ie : ssid, Provider or ip_address
@requirements : pip install plotly
@author : Paul Pfeffer
"""

import re
import datetime
import itertools
import plotly
import SpeedTester


class DrawSpeed(object):
    """Draw SpeedTester data."""

    def __init__(self, speeddata):
        """Initialize main data and some regexes."""
        super(DrawSpeed, self).__init__()
        self.speeddata = speeddata
        self.datetime_regex = "(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)"
        self.number = "(\d.+)(M|m)"

    def parsedata(self, parsedays=True):
        """Parse speedtester data into local variables."""
        self.x_axis = []
        self.upload_speeds = []
        self.download_speeds = []
        self.ping_speeds = []
        self.ssid_names = []
        self.uids = []
        for key, val in sorted(self.speeddata.iteritems()):
            d = re.search(self.datetime_regex, key)
            self.x_axis.append(datetime.datetime(
                year=int(d.group(1)),
                month=int(d.group(2)),
                day=int(d.group(3)),
                hour=int(d.group(4)),
                minute=int(d.group(5)),
                second=int(d.group(6)))
            )
            self.upload_speeds.append(float(re.search(self.number, val["upload"]).group(1)))
            self.download_speeds.append(float(re.search(self.number, val["download"]).group(1)))
            self.ping_speeds.append(float(re.search(self.number, val["ping"]).group(1)))
            self.ssid_names.append(val["ssid"])
        if not parsedays:
            self.x_axis = [item.replace(year=2000, month=1, day=1) for item in self.x_axis]

    def filter_data(self, filter_key, filter_value):
        """
        Filter out specific key value pairs from data collected.

        @param filter_key all keys are available for filtering however
         the only ones that make sense are : (ssid, Provider)
        """
        new_data = {}
        for date, data in self.speeddata.iteritems():
            keep_data = False
            for key, val in data.iteritems():
                if key.strip() == filter_key and val.strip() == filter_value:
                    keep_data = True
            if keep_data:
                new_data[date] = data
        self.speeddata = new_data

    def gettemplatetrace(self, graph):
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
            x=self.x_axis,
            text=display_text,
            mode='lines+markers',
            line=dict(
                shape='spline'
            ),
            marker=plotly.graph_objs.Marker(
                size=5,
                line=plotly.graph_objs.Line(width=1.0), opacity=0.5
            )
        )

    def formdata(self, graph):
        """
        Initialize data by with the trace types provided in graph.

        @param graph A string or list of strings containing the data types to graph
                        Current options : download, upload
        """
        data = []
        if ("download" in graph):
            y_axis = self.download_speeds
            y_name = "Download"
            download_trace = self.gettemplatetrace(graph)
            setattr(download_trace, "y", y_axis)
            setattr(download_trace, "name", y_name)
            data.append(download_trace)
            # setattr(download_trace, "uid", self.download_ids)
        if ("upload" in graph):
            y_axis = self.upload_speeds
            y_name = "Upload"
            upload_trace = self.gettemplatetrace(graph)
            setattr(upload_trace, "y", y_axis)
            setattr(upload_trace, "name", y_name)
            data.append(upload_trace)
        self.data = data

    def setuplayout(self):
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

    def drawdata(self):
        """Call to set up layout and plotly plot to make html page."""
        self.setuplayout()
        fig = plotly.graph_objs.Figure(data=self.data, layout=self.layout)
        plotly.offline.plot(fig, filename='..\Mgmt\speedresults.html')


def main():
    """Example of how to use the class."""
    i_speed = SpeedTester.SpeedTester()
    i_speed.get_previous_results()
    d_speed = DrawSpeed(i_speed.results)
    d_speed.filter_data("ssid", "NETGEAR49-5G")
    d_speed.parsedata(parsedays=True)
    # d_speed.formdata(["download", "upload"])
    d_speed.formdata(["download"])
    d_speed.drawdata()
if __name__ == '__main__':
    main()
