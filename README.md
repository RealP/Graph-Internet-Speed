# Graph-Internet-Speed
Run and visualize speedtest data.

Set up the program to run in loop either using a cronjob or using the included runner script. When the program runs it saves the upload, download, ping, ssid and other information to a json file. These json can be generated into interactive plotly or matplotlib graphs by running the DrawSpeed.py module. 

## Command line arguments

### Run

    usage: runner.py run [-h] -f FREQUENCY FREQUENCY [-d DURATION DURATION]
                         [-resultfile RESULTFILE] [-configfile CONFIGFILE]
                         [-pidfile PIDFILE]

    Measure internet speed periodically by setting frequency and duration.

    optional arguments:
      -h, --help            show this help message and exit
      -f FREQUENCY FREQUENCY, --frequency FREQUENCY FREQUENCY
                            How often should we run.
      -d DURATION DURATION, --duration DURATION DURATION
                            How long should we run. (default=[24, 'hour'])
      -resultfile RESULTFILE
                            Location where results shouls be saved
                            (default=speedresults.json)
      -configfile CONFIGFILE
      -pidfile PIDFILE

    Both frequency and duration should be formatted as follows -----------
    interger [sec|min|hour|day|] ex) 5 min


### Draw
 
    usage: runner.py draw [-h] [-resultfile RESULTFILE] [-type {pyplot,plotly}]
                          [-filter FILTER FILTER] [-options {download,upload}]

    optional arguments:
      -h, --help            show this help message and exit
      -resultfile RESULTFILE
                            Choose results file to draw.
                            (default=speedresults.json)
      -type {pyplot,plotly}
                            The type of graph to display (default=pyplot)
      -filter FILTER FILTER
                            Filter data on specific key value pairs
      -options {download,upload}
                            Graph upload or download speeds. (default=download)


### Examples
eg) Run every 5 minutes for the next 24 hours saving results on desktop. (be sure this file exists)

    python runner.py run -f 5 min -d 24 hour -resultfile /path/to/result/file

eg) Draw the results of a speedtest run.

    python runner.py draw -resultfile /path/to/result/file

## Modules
### SpeedTester.py
Main class which gets data on your internet speed.
#### SpeedTester
> Get the speed of Internet.

- \_\_del\_\_
- get\_previous\_results
- run\_test
- parse\_and\_save\_results
  - Parse results into the available keys.
- write\_results\_to\_file
  - Write the gathered results to a text file.

#### DrawSpeed.py

This is for for graphing the results of the SpeedTester

Currently you can create both plotly and matplotlib graphs, but the user interface is not very friendly. At this point if you want to modify the graphs you'll need to read/modify the main function. Otherwise just

    python DrawSpeed.py

Some sample graphs. (Data not very interesting)
![Plotly Graph](data/plotly.png "Plotly Graph Example")
![PyPlot Graph](data/pyplot.png "PyPlotP Graph Example")
