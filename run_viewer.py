# myapp.py

import glob
from random import random
from collections import defaultdict

import tensorflow as tf
import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import Button, Column, MultiChoice, MultiSelect, Select, CheckboxButtonGroup, RadioGroup, Line
from bokeh.models import ColumnDataSource
from bokeh.palettes import RdYlBu3
from bokeh.plotting import curdoc, figure
from bokeh.models.glyph import LineGlyph

class RunViewer:

    def __init__(self, log_dir='./runs/*'):
        self.log_dir = log_dir
        self.runs_paths = glob.glob(log_dir)
        self.data_sources = self.parse_data_sources(self.runs_paths)
        self.viewer = self.create_viewer()

    def parse_data_sources(self, runs):
        data_sources = defaultdict(dict)
        for run_path in runs:
            run_df = self.run_to_df(run_path)
            sources = run_df.groupby('tag')
            data_sources[run_path]["tags"] = {name: group for name, group in sources}
        return data_sources

    def run_to_df(self, run_path):
        event_records = []
        for event in tf.compat.v1.train.summary_iterator(run_path):
            if len(event.summary.ListFields()) == 1:
                wall_time = event.wall_time
                tag = event.summary.value[0].tag
                val = event.summary.value[0].simple_value
                step = getattr(event, 'step', 0)
                event_records.append((step, wall_time, tag, val))
        return pd.DataFrame.from_records(event_records, columns=['step', 'wall_time', 'tag', 'value'])

    def clear_run_plots(self, run_name):
        for cur_tag, line in self.data_sources[run_name]["lines"].items():
            line.visible = False

    def _show_tags(self, run_name):
        def inner():
            # Switch the tags on and off again.
            current_vis = self.data_sources[run_name]["tag_boxes"].visible
            self.data_sources[run_name]["tag_boxes"].visible = not current_vis
            if current_vis:
                print("Clearing plot!")
                self.clear_run_plots(run_name)


            if self.data_sources[run_name]["loaded"]:
                print("Lines already loaded into data sources!")
                return
            # Generates lines for each of the possible tags.
            self.data_sources[run_name]["lines"] = {}
            for cur_tag, tag_data in self.data_sources[run_name]["tags"].items():
                key = f"{run_name}:{cur_tag}"
                print(f"Making line for {key}")
                # identifier for current tag.
                x_label = f'step_{key}'
                # add tag data, and step data to data source. (x, y)
                data_source.add(tag_data.value.values, cur_tag)
                data_source.add(tag_data.step.values, x_label)
                # Store line away.
                line = comp_figure.line(x_label, cur_tag, source=data_source, name=f'{run_name}:{cur_tag}', legend_label=cur_tag)
                line.visible = False
                self.data_sources[run_name]["lines"][cur_tag] = line

            self.data_sources[run_name]["loaded"] = True
        return inner

    def _plot_tag(self, run_name, tag_names):
        def inner(attr, old, new):
            print('attr', old, new)
            # Calculate sets needed to add and remove from all.
            old, new = set(old), set(new)
            take_out = old.difference(new)
            put_in = new.difference(old)
            print(take_out)

            # Remove tag info from fig.
            for out_ix in take_out:
                cur_tag = tag_names[out_ix]
                self.data_sources[run_name]["lines"][cur_tag].visible = False
                print(f"Removing {cur_tag}")
            print(put_in)
            # Add tag info to fig.
            for in_ix in put_in:
                cur_tag = tag_names[in_ix]
                self.data_sources[run_name]["lines"][cur_tag].visible = True
                print(f"Adding {cur_tag}")
        return inner

    def create_viewer(self):
        runs = []
        for f_name, run_info in self.data_sources.items():
            # Construct button and apply callback to them.
            run_button = Button(label=f_name, name=f_name, button_type='primary')
            run_button.on_click(self._show_tags(f_name))
            runs.append(run_button)
            # Generate check boxes for tags.
            tag_names = list(run_info["tags"].keys())
            tags = CheckboxButtonGroup(labels=tag_names)
            tags.visible = False
            # tags.on_click(self._plot_tag(f_name, tag_names))
            tags.on_change('active', self._plot_tag(f_name, tag_names))
            runs.append(tags)
            # Captrue both button and tag models for later modificaiton.
            self.data_sources[f_name]["run_button"] = run_button
            self.data_sources[f_name]["tag_boxes"] = tags
            self.data_sources[f_name]["loaded"] = False
        return column(runs)

data_source = ColumnDataSource(data=dict())
tools = 'pan,wheel_zoom,xbox_select,reset'
comp_figure = figure(plot_width=900, plot_height=900, tools=tools, active_drag="xbox_select")


RV = RunViewer('./runs/*')
viewer = RV.create_viewer()

# put the button and plot in a layout and add to the document
curdoc().add_root(column(comp_figure, viewer))
curdoc().title='Run Comparision'

