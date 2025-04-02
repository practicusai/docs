---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Plotting with Multiple Layers

In this example we are going to give you a brief tutorial of how to use multiple graphics on one figure by using bokeh.

We are going to cover these topics:
- How to create and edit a figure
- How to process multiple glyphs (graphs) over a figure
- How to add dynamic explanations over glyphs
- How to create _Bar_ and _Line_ plot

## Before you begin

At the time of this writing, Bokeh only support `Jupyter Lab` and not `VS Code` [View issue details](https://github.com/bokeh/bokeh/issues/10765) Please make sure you run this example in Jupyter Lab, or verify on Bokeh repo that the issue is resolved.



Let's begin by importing our libraries

```python
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import ColumnDataSource, HoverTool
import practicuscore as prt
```

Here's a breakdown of each bokeh function we've imported:

1. bokeh.plotting
    - figure: Creates a new Bokeh plot with customizable options such as plot size, title, axis labels, etc.
    - show: Displays a Bokeh plot in the current environment, such as a browser or a Jupyter notebook.
    - output_notebook: Configures Bokeh to display plots directly in Jupyter notebooks.
2. bokeh.models
    - ColumnDataSource: A data structure that holds the data to be plotted and facilitates efficient updating and sharing of data between different plot elements.
    - HoverTool: A tool that provides interactive hover tooltips, displaying additional information about data points when the mouse cursor hovers over them

```python
worker = prt.get_local_worker()
```

One of the most illustrative datasets for demonstrating multiple layer analyze is the Iris dataset.

The Iris dataset is a popular dataset in machine learning and statistics, often used for classification tasks. It consists of 150 samples of iris flowers, each belonging to one of three species: Setosa, Versicolor, or Virginica. Within this data set we will use both Bar and Circle graphic style from Plot. The dataset comprises four features, each representing measurements of the length and width of both the petals and sepals of flowers.

Let's load it into one of our worker environments.

```python
data_set_conn = {
    "connection_type": "WORKER_FILE",
    "sample_size": 150,
    "file_path": "/home/ubuntu/samples/data/iris.csv"
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

Before starting data analyzing with bokeh, we need to do some preprocess on Iris dataset

```python
means = df.groupby('species').mean().reset_index()
```

```python
from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()

means['species_encoded'] = label_encoder.fit_transform(means['species'])
```

```python
means
```

To display Bokeh plots inline in a classic Jupyter notebook, use the [output_notebook()](https://docs.bokeh.org/en/2.4.1/docs/user_guide/jupyter.html) function from bokeh.io.

```python
output_notebook()
```

We need to create a data structure that holds the data to be plotted to use Bokeh more efficiently. For this we will use [ColumnDataSource()](https://docs.bokeh.org/en/latest/docs/reference/models/sources.html#bokeh.models.ColumnDataSource) function of Bokeh.

```python
source = ColumnDataSource(means)
```

Let's create our figure to do some visualisation.

```python
p = figure(title="Analysis Over Species", x_axis_label='Species', y_axis_label='Features', width=400, height=300)
```

Here's an explanation of each parameter in the figure function call:

- title: Sets the title of the plot. In this case, it's set to "Analysis Over Species". The title is displayed at the top of the plot.
- x_axis_label: Specifies the label for the x-axis. It provides information about the data represented on the x-axis. In this case, it's set to 'Species', indicating that the x-axis represents different species.
- y_axis_label: Specifies the label for the y-axis. Similar to x_axis_label, it provides information about the data represented on the y-axis. Here, it's set to 'Features', indicating that the y-axis represents various features.
- width: Sets the width of the plot in pixels. In this case, it's set to 400 pixels, determining the horizontal size of the plot.
- height: Sets the height of the plot in pixels. Here, it's set to 300 pixels, determining the vertical size of the plot.

Let's continue with our first plotting of _vbar_ (vertical bar plotting)!

```python
first_layer = p.vbar(x = 'species_encoded', top = 'sepal_length', width=0.9, line_color='green', fill_color='lime', fill_alpha=0.5, legend_label="Sepal Length", source=source)
show(p)
```

Here's an explanation of each _vbar_ parameters:

- p: This is the figure object where the plot will be added.
- vbar: This is the glyph function used to create vertical bar glyphs (rectangles) on the plot.
- x: This parameter specifies the x-coordinates of the bars.
- top: This parameter specifies the top edge of each bar.
- width: This parameter determines the width of the bars. Here, it's set to _0.9_, indicating that the bars will have a width of 0.9 units along the x-axis.
- line_color: This parameter sets the color of the outline of the bars. It's set to _'green'_, giving the bars a green outline.
- fill_color: This parameter sets the fill color of the bars. It's set to _'lime'_, giving the bars a lime green color.
- fill_alpha: This parameter sets the transparency of the fill color. It's set to _0.5_, making the bars partially transparent.
- legend_label: This parameter sets the label for the legend entry corresponding to this glyph. It's set to _"Sepal Length"_, which will be displayed in the legend.
- source: This parameter specifies the data source from which the glyph will pull its data. It's set to _source_, which is defined previously by using ColumnDataSource().

Overall, this line of code creates a vertical bar plot of sepal lengths for different species, with customization for appearance and legend labeling, and it adds this plot as a layer to the existing figure p. You can check out bokeh [documentation of colors](https://docs.bokeh.org/en/latest/docs/reference/colors.html) for more coloring options.


Let's add another vbar, a second layer, which will show case _petal_length_.

```python
second_layer = p.vbar(x = 'species_encoded', top = 'petal_length', width=0.9, line_color='blue', fill_color='lightskyblue', fill_alpha=0.5, legend_label="Petal Length", source=source)
show(p)
```

After adding our second layer it started to be too crowded for such a small figure frame, let's expand it and we could also use some more explanatory labels for axis.

```python
p.width = 800
p.height = 600
p.xaxis.axis_label = 'Flower Species'
p.yaxis.axis_label = 'Flower Features'

show(p)
```

Let's add some plots about our flowers width, but if we add more bars it will make the figure too confusing to read. Therefore, let's add line plots to visualize width features of our flowers.

```python
third_layer = p.line(x='species_encoded', y='sepal_width', line_width=4, line_color='darkolivegreen', legend_label="Sepal Width", source=source)
show(p)
```

Here's an explanation of each _line_ parameters:

- p: This is the figure object where the line plot will be added.
- line: This is the glyph function used to create line glyphs on the plot.
- x: This parameter specifies the x-coordinates of the line.
- y: This parameter specifies the y-coordinates of the line.
- line_width: This parameter determines the width of the line. It's set to _4_, indicating that the line will be drawn with a width of 4 units.
- line_color: This parameter sets the color of the line. It's set to _'darkolivegreen'_, giving the line a dark olive green color.
- legend_label: This parameter sets the label for the legend entry corresponding to this glyph. It's set to _"Sepal Width"_, which will be displayed in the legend.
- source: This parameter specifies the data source from which the glyph will pull its data.  It's set to _source_, which is defined previously by using ColumnDataSource().

Overall, this line of code creates a line plot of sepal widths for different species, with customization for appearance and legend labeling, and it adds this plot as a layer to the existing figure p.


Let's add our fourth and last plot!

```python
fourth_layer = p.line(x='species_encoded', y='petal_width', line_width=4, line_color='darkblue', legend_label="Petal Width", source=source)
show(p)
```

After adding all layer we still missing something, it would be a cool feature if we could see the values of data points. Actually, we could use _HoverTool()_ bokeh to do that!

```python
tips = [
    ('Sepal Length', '@sepal_length'),
    ('Petal Length', '@petal_length'),
    ('Sepal Width', '@sepal_width'),
    ('Petal Width', '@petal_width')
]

p.add_tools(HoverTool(tooltips=tips)) 
show(p)
```

Right now, when we hover over plots we could see the values of data points.

Let's break down the code we have used:

- tips: This is a list of tuples, where each tuple contains two elements. The first element of each tuple represents the label for the tooltip, and the second element represents the data field from the data source (_source_) to be displayed in the tooltip. For example, _Sepal Length_ is the label for the tooltip, and _@sepal_length_ instructs Bokeh to display the value of the _sepal_length_ column from the data source (_source_) when hovering over a data point
- p.add_tools: This method adds tools to the plot (p). Here, we're adding the HoverTool to enable hover tooltips.
- HoverTool: This is a tool provided by Bokeh for adding hover functionality to plots. It displays additional information when the mouse cursor hovers over a data point.
- tooltips=tips: This parameter of the HoverTool constructor specifies the tooltips to be displayed when hovering over data points. We pass the tips list, which contains the tooltip labels and data fields.


Last but not least, we could remove layers by using their _visible_ parameter:

```python
first_layer.visible = False
show(p)
```

```python
first_layer.visible = True
show(p)
```

That was the end. You can always checkout our other notebooks about plotting or [documentation of bokeh](https://docs.bokeh.org/en/2.4.3/index.html) to see more!

```python
proc.kill()
```


---

**Previous**: [Introduction](introduction.md) | **Next**: [Eda > Analyze](../eda/analyze.md)
