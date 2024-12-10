---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Dynamic Size & Color


In this notebook we are going to give you a brief tutorial on how to use color and size feature of glyphs (a.k.a graphs and plots) dynamically by assigning features of dataset to color and size parameters.

- How to create figure
- How to create and edit _circle_ plots 
- How to add dynamic explanations over glyphs

```python
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import LinearColorMapper, ColumnDataSource, ColorBar, HoverTool
from bokeh.transform import transform
import practicuscore as prt
import pandas as pd
import numpy as np
```

Here's a breakdown of each bokeh function we've imported:

1. bokeh.plotting:
    - figure: This module provides a high-level interface for creating Bokeh plots. It includes functions for creating and customizing figures, such as setting titles, axis labels, plot size, and other visual properties.
    - show: This function displays a Bokeh plot in the current environment, such as a browser or a Jupyter notebook.
    - output_notebook: This function configures Bokeh to display plots directly within Jupyter notebooks.
2. bokeh.models:
    - ColumnDataSource: This module contains a collection of classes and functions representing various components of a Bokeh plot, such as glyphs (shapes representing data points), axes, grids, annotations, and tools. ColumnDataSource is a fundamental data structure in Bokeh that holds the data to be plotted and allows for efficient updating and sharing of data between different plot elements.
    - HoverTool: This module provides a tool for adding interactive hover tooltips to Bokeh plots. It allows users to display additional information about data points when the mouse cursor hovers over them.
    - LinearColorMapper: A mapper that maps numerical data to colors in a linear manner. It's often used to color glyphs based on a continuous range of data values.
    - ColorBar: A color bar that provides a visual representation of the mapping between data values and colors, often used with LinearColorMapper
3. bokeh.transform:
    - transform: This function is used to apply a transformation to the data in a column of a ColumnDataSource. It takes two arguments, 
        - column_name: The name of the column in the ColumnDataSource to transform.
        - transform_expression: A JavaScript expression defining the transformation to apply to the data. This expression can involve mathematical operations, functions, or other JavaScript constructs.

```python
worker = prt.get_local_worker()
```

One of the most illustrative datasets for demonstrating dynamic size and color is the Titanic dataset.

The Titanic dataset is a popular dataset used in machine learning and data analysis. It contains information about passengers aboard the RMS Titanic, including whether they survived or not. Within this data set we will use columns of pclass, fare, age and survived. Let's describe what these columns means for better understanding.

- Pclass: Ticket class (1 = 1st, 2 = 2nd, 3 = 3rd).
- Fare: Passenger fare.
- Age: Passenger's age in years.
- Survived: Indicates whether the passenger survived or not (0 = No, 1 = Yes).

Let's load it into one of our worker environments.

```python
data_set_conn = {
    "connection_type": "WORKER_FILE",
    "sample_size": 1180,
    "file_path": "/home/ubuntu/samples/titanic.csv"
}
```

```python
proc = worker.load(data_set_conn, engine='AUTO') 
```

```python
proc.wait_until_done(timeout_min=600)
proc.show_logs()
```

```python
df = proc.get_df_copy()
display(df)
```

To display Bokeh plots inline in a classic Jupyter notebook, use the [output_notebook()](https://docs.bokeh.org/en/2.4.1/docs/user_guide/jupyter.html) function from bokeh.io.

```python
output_notebook()
```

We need to create a data structure that holds the data to be plotted to use Bokeh more efficiently. For this we will use [ColumnDataSource()](https://docs.bokeh.org/en/latest/docs/reference/models/sources.html#bokeh.models.ColumnDataSource) function of Bokeh.

```python
source = ColumnDataSource(df)
```

We need to create a mapper of colors to use color feature as dynamically. We will use LinearColorMapper() built-in function of Bokeh to create our mapper.

```python
color_mapper = LinearColorMapper( 
    palette='Sunset11', 
    low=df['survived'].min(), 
    high=df['survived'].max()
)
```

Here's a breakdown of the parameters:

- palette: This parameter specifies the color palette to use for mapping the data values. In this case, it's set to 'Sunset11', which is refers to a predefined color palette named 'Sunset11' of Bokeh. This palette consists of 11 distinct colors arranged in a gradient from light to dark or from one color to another. You can look at [Bokeh's documentation](#https://docs.bokeh.org/en/latest/docs/reference/palettes.html) to see more options.
- low: This parameter sets the lowest data value in the range of values to be mapped to colors. It's typically set to the minimum value of the data being mapped. In this case, it's set to df['survived'].min(), indicating that the lowest value in the 'survived' column of the DataFrame (df) will be mapped to the lowest color in the palette.
- high: This parameter sets the highest data value in the range of values to be mapped to colors. It's typically set to the maximum value of the data being mapped. Here, it's set to df['survived'].max(), indicating that the highest value in the 'survived' column of the DataFrame (df) will be mapped to the highest color in the palette.

Let's create our figure to do some visualisatoin.

```python
p = figure(title="Analysis Over Survivors", x_axis_label='age', y_axis_label='fare', width=600, height=400)
```

Here's an explanation of each parameter in the figure function call:

- title: Sets the title of the plot. In this case, it's set to "Analysis Over Survivors". The title is displayed at the top of the plot.
- x_axis_label: Specifies the label for the x-axis. It provides information about the data represented on the x-axis. In this case, it's set to 'age', indicating that the x-axis represents age of travellers.
- y_axis_label: Specifies the label for the y-axis. Similar to x_axis_label, it provides information about the data represented on the y-axis. Here, it's set to 'fare', indicating that the y-axis represents paid fares of travellers.
- width: Sets the width of the plot in pixels. In this case, it's set to 400 pixels, determining the horizontal size of the plot.
- height: Sets the height of the plot in pixels. Here, it's set to 300 pixels, determining the vertical size of the plot.

Let's continue with our first plotting of _circle_ (circle plotting)!

```python
circle = p.circle(x='age', y='fare', radius='pclass', color=transform('survived', color_mapper), alpha=0.5, source=source)
show(p)
```

Here's an explanation of each parameter:

- p: This is the figure object where the circles will be added. It seems like p is previously defined as a figure with certain settings like title, axis labels, etc.
- circle: This variable stores the result of the p.circle function call, representing the circles added to the plot.
- x: This parameter specifies the x-coordinates of the circles. It's mapped to the 'age' column in the data source (source), indicating the position of each circle along the x-axis.
- y: This parameter specifies the y-coordinates of the circles. It's mapped to the 'fare' column in the data source (source), indicating the position of each circle along the y-axis.
- radius: This parameter specifies the radius of the circles. It's mapped to the 'pclass' column in the data source (source), indicating the radius of each circle.
- color: This parameter specifies the color of the circles. Here, it's set to transform('survived', color_mapper).
- transform('survived', color_mapper): This function applies the color mapping defined by the LinearColorMapper object (color_mapper) to the 'survived' column in the data source (source). The color of each circle will be determined by the value in the 'survived' column, mapped to colors based on the color_mapper.
- alpha: This parameter sets the transparency of the circles. It's set to 0.5, making the circles partially transparent.
- source: This parameter specifies the data source from which the circles will pull their data. It's set to source, which is likely a ColumnDataSource object containing the data needed to plot the
 circles.

At this point we should add a bar which describes the meaning of colors. We could do this by using ColorBar() feature of Bokeh.

```python
color_bar = ColorBar(color_mapper=color_mapper, padding=3,
                         ticker=p.xaxis.ticker, formatter=p.xaxis.formatter)

p.add_layout(color_bar, 'right')
show(p)
```

Here's an explanation of each parameter:

- color_mapper: This parameter specifies the LinearColorMapper object (color_mapper) that defines the mapping between data values and colors. The color bar will use this mapper to display the range of colors corresponding to the range of data values.
- padding: This parameter sets the padding (in pixels) between the color bar and other elements of the plot. It's set to 3 pixels in this case, providing some space around the color bar.
- ticker: This parameter specifies the ticker to use for labeling the color bar axis. It's set to p.xaxis.ticker, which likely means that the same ticker used for the x-axis of the plot (p) will be used for the color bar axis.
- formatter: This parameter specifies the formatter to use for formatting the tick labels on the color bar axis. It's set to p.xaxis.formatter, meaning that the same formatter used for the x-axis of the plot (p) will be used for the color bar axis.
- p.add_layout: This method adds a layout element to the plot (p). Here, we're adding the color bar to the plot.
- color_bar: This is the ColorBar object that we created earlier, representing the color bar to be added to the plot.
- 'right': This parameter specifies the location where the color bar will be added relative to the plot. Here, it's set to 'right', indicating that the color bar will be placed to the right of the plot.


We still missing something, it would be a cool feature if we could see the values of data points. Actually, we could use _HoverTool()_ bokeh to do that!

```python
tips = [
    ('Fare', '@fare'),
    ('Age', '@age'),
    ('Survived', '@survived'),
    ('Pclass', '@pclass')
]

p.add_tools(HoverTool(tooltips=tips)) 
show(p)
```

Right now, when we hover over plots we could see the values of data points.

Let's break down the code we have used:

- tips: This is a list of tuples, where each tuple contains two elements. The first element of each tuple represents the label for the tooltip, and the second element represents the data field from the data source (_source_) to be displayed in the tooltip. For example, _Fare_ is the label for the tooltip, and _@fare_ instructs Bokeh to display the value of the _fare_ column from the data source (_source_) when hovering over a data point
- p.add_tools: This method adds tools to the plot (p). Here, we're adding the HoverTool to enable hover tooltips.
- HoverTool: This is a tool provided by Bokeh for adding hover functionality to plots. It displays additional information when the mouse cursor hovers over a data point.
- tooltips=tips: This parameter of the HoverTool constructor specifies the tooltips to be displayed when hovering over data points. We pass the tips list, which contains the tooltip labels and data fields.


That was the end. You can always checkout our other notebooks about plotting or [documentation of bokeh](https://docs.bokeh.org/en/2.4.3/index.html) to see more!

```python
proc.kill()
```


---

**Previous**: [Legacy Python](../../../04_virtual_environments/02_legacy_python.md) | **Next**: [Multiple Layer Analyze](../Multiple_Layer_Analyze/Multiple_Layer_Analyze.md)
