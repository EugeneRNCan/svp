"""
Description: This script is the implementation of the Real-time plotting function if openSVP. Therefore, you can find
his GUI creation, how does it access to data and everything

note :
The link between this module and ui.py is situated in the op_run method of the EntityTreeEntry Class
"""

import os
import random
import wx
import pandas as pd

import matplotlib

matplotlib.use('WXAgg')
from matplotlib import lines
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab


info_values = {
    'Single phase': ['1'],
    'Three phase': ['1', '2', '3']

}

MARKER = {
    'Point': '.',
    'Circle': 'o',
    'Triangle': '^',
    'Tri': '2',
    'Octagon': '8',
    'Square': 's',
    'Pentagone': 'p',
    'Star': '*',
    'Diamond': 'D',
    'Plus': 'P'
}



class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a
        manual mode with an associated value.
    """

    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)

        self.value = initval

        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.radio_auto = wx.RadioButton(self, -1,
                                         label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
                                           label="Manual")
        self.manual_text = wx.TextCtrl(self, -1,
                                       size=(35, -1),
                                       value=str(initval),
                                       style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)

        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())

    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()

    def is_auto(self):
        return self.radio_auto.GetValue()

    def manual_value(self):
        return self.value

class Preference_canvas(FigCanvas):
    def __init__(self, panel=wx.Panel, size=(0, 0), title='tab'):
        height = 1*size[1]/400
        width = 2*size[0]/300
        self.pref_figure = Figure(figsize=(width, height))
        FigCanvas.__init__(self, panel, -1, self.pref_figure)
        self.second_axes = None
        self.title = title



    def Create_Figure(self, type=None, parameters={}):

        self.type = type
        self.parameters = parameters

        if self.type == 'Time-based':
            self.Time_based_Figure()
        elif self.type == 'XY':
            self.XY_Figure()

    def Time_based_Figure(self):

        self.axes = self.pref_figure.add_subplot(111)
        self.axes.set_facecolor('white')
        self.axes.set_title(self.title)
        self.axes.set_ylabel(self.parameters['y1 axis title'])
        self.axes.set_xlabel(self.parameters['x axis title'])
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        x = list(np.arange(55, 155, 1))

        if self.parameters['y2_axe'] != 'Disabled':
            self.second_axes = self.axes.twinx()
            self.second_axes.set_ylabel(self.parameters['y2 axis title'])
            pylab.setp(self.second_axes.get_yticklabels(), fontsize=8)
            y2 = [6000] * 25 + list(np.arange(6000, 2000, -80)) + [2000] * 25
            if self.parameters['y2 Overlay']:
                self.y2_overlay_max = lines.Line2D(x,
                                              [8000] * 100,
                                              linewidth=1,
                                              color=self.parameters['y2 Overlay Color'],
                                              label='y2 Overlay'
                                              )
                self.y2_overlay_min = lines.Line2D(x,
                                              [1000] * 100,
                                              linewidth=1,
                                              color=self.parameters['y2 Overlay Color']
                                              )
        # example values :

        y1 = [140] * 25 + list(np.arange(140, 290, 3)) + [290] * 25
        if self.parameters['y1 Overlay']:
            self.y1_overlay_max = lines.Line2D(x,
                                          [200] * 100,
                                          linewidth=1,
                                          color=self.parameters['y1 Overlay Color'],
                                          label='y1 Overlay'
                                          )
            self.y1_overlay_min = lines.Line2D(x,
                                          [25] * 100,
                                          linewidth=1,
                                          color=self.parameters['y1 Overlay Color']
                                          )

        self.axes.grid(self.parameters['Grid'])

        if self.parameters['y1 Overlay']:
            self.axes.add_line(self.y1_overlay_min)
            self.axes.add_line(self.y1_overlay_max)

        if self.parameters['y2 Overlay'] and self.parameters['y2_axe'] != 'Disabled':
            self.second_axes.add_line(self.y2_overlay_min)
            self.second_axes.add_line(self.y2_overlay_max)

        self.axes_plot =self.axes.plot(
            x,
            y1,
            linewidth=1,
            color=self.parameters['y1 line Color'],
            label=self.parameters['y1 axis title']
        )
        if self.parameters['legend']:
            self.axes.legend(loc=3)

        if self.parameters['y2_axe'] != 'Disabled':
            self.second_axes_plot = self.second_axes.plot(
                x,
                y2,
                linewidth=1,
                color=self.parameters['y2 line Color'],
                label=self.parameters['y2 axis title']
            )
            if self.parameters['legend']:
                self.second_axes.legend(loc=1)
        self.pref_figure.tight_layout()
        self.draw()

    def Time_based_add_second_axes(self):
        self.second_axes = self.axes.twinx()
        self.second_axes.set_ylabel(self.parameters['y2 axis title'])
        pylab.setp(self.second_axes.get_yticklabels(), fontsize=8)

        x = list(np.arange(55, 155, 1))
        y2 = [6000] * 25 + list(np.arange(6000, 2000, -80)) + [2000] * 25
        if self.parameters['y2 Overlay']:
            self.y2_overlay_max = lines.Line2D(x,
                                          [8000] * 100,
                                          linewidth=1,
                                          color=self.parameters['y2 Overlay Color'],
                                          label='y2 Overlay'
                                          )
            self.y2_overlay_min = lines.Line2D(x,
                                          [1000] * 100,
                                          linewidth=1,
                                          color=self.parameters['y2 Overlay Color']
                                          )
        if self.parameters['y2 Overlay']:
            self.second_axes.add_line(self.y2_overlay_min)
            self.second_axes.add_line(self.y2_overlay_max)
        self.second_axes_plot = self.second_axes.plot(
            x,
            y2,
            linewidth=1,
            color=self.parameters['y2 line Color'],
            label=self.parameters['y2 axis title']
        )
        if self.parameters['legend']:
            self.second_axes.legend(loc=1)
        self.pref_figure.tight_layout()
        self.draw()

    def Time_based_add_y1_overlay(self):
        x = list(np.arange(55, 155, 1))
        self.y1_overlay_max = lines.Line2D(x,
                                           [200] * 100,
                                           linewidth=1,
                                           color=self.parameters['y1 Overlay Color'],
                                           label='y1 Overlay'
                                           )
        self.y1_overlay_min = lines.Line2D(x,
                                           [25] * 100,
                                           linewidth=1,
                                           color=self.parameters['y1 Overlay Color']
                                           )
        self.axes.add_line(self.y1_overlay_min)
        self.axes.add_line(self.y1_overlay_max)

        self.pref_figure.tight_layout()
        self.draw()

    def Time_based_add_y2_overlay(self):
        x = list(np.arange(55, 155, 1))
        self.y2_overlay_max = lines.Line2D(x,
                                      [8000] * 100,
                                      linewidth=1,
                                      color=self.parameters['y2 Overlay Color'],
                                      label='y2 Overlay'
                                      )
        self.y2_overlay_min = lines.Line2D(x,
                                      [1000] * 100,
                                      linewidth=1,
                                      color=self.parameters['y2 Overlay Color']
                                      )
        self.second_axes.add_line(self.y2_overlay_min)
        self.second_axes.add_line(self.y2_overlay_max)

        self.pref_figure.tight_layout()
        self.draw()

    def XY_Figure(self):
        self.axes = self.pref_figure.add_subplot(111)
        self.axes.set_facecolor('white')
        self.axes.set_title(self.title)
        self.axes.set_ylabel(self.parameters['y axis title'])
        self.axes.set_xlabel(self.parameters['x axis title'])
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        x = [90, 91, 92, 93, 95, 97, 98, 99, 100, 102, 103, 105, 106, 108, 110, 112]
        y_plot = [44, 44, 44, 44, 29, 11, 6, 1, 0, -2, -10, -26, -36, -44, -44, -44]

        if self.parameters['Overlay']:
            y = [44, 44, 44, 37, 22.32, 7.66, 0, 0, 0, 0, -7.33, -22, -29.32, -44, -44, -44]
            y_max = []
            y_min = []
            for i in y:
                if i >= 5 or i <= -5:
                    y_max.append(i + 5)
                    y_min.append(i - 5)
                elif -5 < i < 5:
                    y_max.append(5)
                    y_min.append(-5)

            self.overlay_max = lines.Line2D(x,
                                            y_max,
                                           linewidth=1,
                                           color=self.parameters['Overlay Color'],
                                           label='Overlay'
                                           )
            self.overlay_min = lines.Line2D(x,
                                           y_min,
                                           linewidth=1,
                                           color=self.parameters['Overlay Color']
                                           )

        self.axes.grid(self.parameters['Grid'])

        if self.parameters['Overlay']:
            self.axes.add_line(self.overlay_min)
            self.axes.add_line(self.overlay_max)

        self.axes_plot = self.axes.plot(
            x,
            y_plot,
            linewidth=0,
            marker=MARKER[self.parameters['marker type']],
            color=self.parameters['marker Color'],
            label=self.parameters['y axis title']
        )

        self.pref_figure.tight_layout()
        self.draw()

    def XY_add_overlay(self):
        x = [90, 91, 92, 93, 95, 97, 98, 99, 100, 102, 103, 105, 106, 108, 110, 112]
        y = [44, 44, 44, 37, 22.32, 7.66, 0, 0, 0, 0, -7.33, -22, -29.32, -44, -44, -44]
        y_max = []
        y_min = []
        for i in y:
            if i >= 5 or i <= -5:
                y_max.append(i + 5)
                y_min.append(i - 5)
            elif -5 < i < 5:
                y_max.append(5)
                y_min.append(-5)

        self.overlay_max = lines.Line2D(x,
                                        y_max,
                                        linewidth=1,
                                        color=self.parameters['Overlay Color'],
                                        label='Overlay'
                                        )
        self.overlay_min = lines.Line2D(x,
                                        y_min,
                                        linewidth=1,
                                        color=self.parameters['Overlay Color']
                                        )
        self.axes.add_line(self.overlay_min)
        self.axes.add_line(self.overlay_max)

        self.pref_figure.tight_layout()
        self.draw()

class GraphFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'Demo: dynamic matplotlib graph'

    def __init__(self, rtp_conn = None):
        wx.Frame.__init__(self, None, -1, self.title)

        self.rtp_conn = rtp_conn
        self.df = pd.DataFrame()
        self.df_x = pd.DataFrame()
        self.df_y = pd.DataFrame()
        self.xy_df = pd.DataFrame()
        self.x_list = []
        self.info = None
        self.show_frame = False
        self.xy = None

        self.xy_list = []
        self.xy_plots = None
        self.xy_plot_enable = False
        self.xy_plot_data = None
        self.xy_plot_first_index = None
        self.new_xy_plot = False
        self.xy_plot_nbr = 0
        self.dpi = 100
        self.paused = False

        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        self.redraw_timer.Start(40)

    def create_menu(self):
        self.menubar = wx.MenuBar()

        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        while self.show_frame is False:
            self.data_read()
        self.init_time_plot()
        self.canvas_time = FigCanvas(self.panel, -1, self.fig_time)
        self.canvas_xy = FigCanvas(self.panel, -1, self.fig_xy)

        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)
        self.ymin2_control = BoundControlBox(self.panel, -1, "Y min (right)", 0)
        self.ymax2_control = BoundControlBox(self.panel, -1, "Y max (right)", 100)

        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)

        self.cb_grid = wx.CheckBox(self.panel, -1,
                                   "Show Grid",
                                   style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)

        self.cb_xlab = wx.CheckBox(self.panel, -1,
                                   "Show X labels",
                                   style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)
        self.cb_xlab.SetValue(True)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin2_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax2_control, border=5, flag=wx.ALL)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas_xy, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.canvas_time, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def data_read(self):
        data = None
        try:
            if self.rtp_conn:
                if self.rtp_conn.poll() is True:
                    data = self.rtp_conn.recv()
        except Exception as e:
            raise
        if data is not None:
            if isinstance(data, type(pd.DataFrame())) is False:
                self.new_xy_plot = True
                if 'VW' in data['name']:
                    self.info = {
                        'name': 'VW',
                        'x': ['AC_VRMS_' + x for x in info_values[data['phases']]],
                        'y': ['AC_P_' + x for x in info_values[data['phases']]],
                        'x_mag': 10,
                        'y_mag': 1000,
                        'fmt': {'x': '-', 'y': '-'}
                    }
                elif 'VV' in data['name']:
                    self.info = {
                        'name': 'VV',
                        'x': ['AC_VRMS_' + x for x in info_values[data['phases']]],
                        'y': ['AC_Q_' + x for x in info_values[data['phases']]],
                        'x_mag': 10,
                        'y_mag': 1000,
                        'fmt': {'x': '-', 'y': '-'}
                    }
                elif 'FW' in data['name']:
                    self.info = {
                        'name': 'FW',
                        'x': ['AC_FREQ_' + x for x in info_values[data['phases']]],
                        'y': ['AC_P_' + x for x in info_values[data['phases']]],
                        'x_mag': 1,
                        'y_mag': 1000,
                        'fmt': {'x': '-', 'y': '-'}
                    }
                elif 'CPF' in data['name']:
                    self.info = {
                        'name': 'CPF',
                        'x': ['AC_PF_' + x for x in info_values[data['phases']]],
                        'y': ['AC_INC_' + x for x in info_values[data['phases']]],
                        'x_mag': 1,
                        'y_mag': 1,
                        'fmt': {'x': '-', 'y': 'o'}
                    }
                else:
                    self.info = {
                        'name': 'invalid Script name (CPF, VW, VV, FW in title)',
                        'x': ['AC_VRMS_' + x for x in info_values[data['phases']]],
                        'y': ['AC_IRMS_' + x for x in info_values[data['phases']]],
                        'x_mag': 10,
                        'y_mag': 1,
                        'fmt': {'x': '-', 'y': '-'}
                    }

            else:
                self.df = self.df.append(data)

                if len(self.info['x']) > 1:
                    a = data[self.info['x'][0]].astype(float) + data[self.info['x'][1]].astype(float) + data[self.info['x'][2]].astype(float)
                    a.name = self.info['x'][0][:-2]
                    self.df_x = self.df_x.append(a)
                else:
                    self.df_x = self.df_x.append(data[self.info['x']].astype(float))
                if len(self.info['y']) > 1:
                    a = data[self.info['y'][0]].astype(float) + data[self.info['y'][1]].astype(float) + data[self.info['y'][2]].astype(float)
                    a.name = self.info['y'][0][:-2]
                    self.df_y = self.df_y.append(a)
                else:
                    self.df_y = self.df_y.append(data[self.info['y']].astype(float))

                self.x_list.append((self.df.index[-1] - self.df.index[0]).total_seconds())
                if self.new_xy_plot is True:
                    self.fig_xy = Figure((10.0, 5), dpi=self.dpi)
                    #self.fig_xy.tight_layout()
                    if self.xy is not None:
                        self.xy_df = pd.DataFrame()
                        self.xy_list.append(self.xy_plot_data)
                        self.vbox.Hide(self.canvas_xy)
                        self.vbox.Remove(0)
                        self.canvas_xy = FigCanvas(self.panel, -1, self.fig_xy)
                        self.vbox.Insert(0, self.canvas_xy, 1, flag=wx.LEFT | wx.TOP | wx.GROW,)
                        self.vbox.Fit(self)
                    self.init_xy_plot()
                self.show_frame = True

    def init_xy_plot(self):
        # adding the x y plot


        if len(self.xy_list) == 0:
            self.xy_plots = self.fig_xy.subplots(1, 1, squeeze=False)
            self.xy = [0, 0]
        else:
            a = -1
            r = list(range(0, int(np.ceil((len(self.xy_list) + 1) * 0.25))))
            r.reverse()
            if len(self.xy_list) < 4:
                self.xy_plots = self.fig_xy.subplots(1, len(self.xy_list) + 1, squeeze=False)
            else:
                self.xy_plots = self.fig_xy.subplots(int(np.ceil((len(self.xy_list) + 1)*0.25)), 4, squeeze=False)
            for i in r:
                for j in range(0, 4):
                    a += 1
                    if a == len(self.xy_list):
                        self.xy = [i, j]
                        break
                    else:
                        self.xy_plots[i][j].set_facecolor(self.xy_list[a].axes.get_facecolor())
                        self.xy_plots[i][j].set_title(self.xy_list[a].axes.get_title(), size=8)
                        self.xy_plots[i][j].set_ylabel(self.xy_list[a].axes.get_ylabel())
                        self.xy_plots[i][j].set_xlabel(self.xy_list[a].axes.get_xlabel())
                        self.xy_plots[i][j].grid(True, color='gray')
                        pylab.setp(self.xy_plots[i][j].get_xticklabels(), fontsize=6)
                        pylab.setp(self.xy_plots[i][j].get_yticklabels(), fontsize=6)
                        self.xy_plots[i][j].plot(
                            self.xy_list[a].get_data()[0],
                            self.xy_list[a].get_data()[1],
                            self.xy_list[a].get_marker(),
                            linewidth=self.xy_list[a].get_linewidth(),
                            color=self.xy_list[a].get_color()
                        )[0]


        self.xy_plot_nbr += 1
        self.xy_plots[self.xy[0]][self.xy[1]].set_facecolor('white')
        self.xy_plots[self.xy[0]][self.xy[1]].set_title('xy Graph of ' + self.info['name'] + ' test' + str(self.xy_plot_nbr), size=8)
        self.xy_plots[self.xy[0]][self.xy[1]].set_ylabel(self.df_y.columns[0])
        self.xy_plots[self.xy[0]][self.xy[1]].set_xlabel(self.df_x.columns[0])
        self.xy_plots[self.xy[0]][self.xy[1]].grid(True, color='gray')

        self.fig_xy.tight_layout()
        pylab.setp(self.xy_plots[self.xy[0]][self.xy[1]].get_xticklabels(), fontsize=8)
        pylab.setp(self.xy_plots[self.xy[0]][self.xy[1]].get_yticklabels(), fontsize=8)


        self.new_xy_plot = False

    def init_time_plot(self):


        # adding the time domain plot

        self.fig_time = Figure((10.0, 2.5), dpi=self.dpi)
        self.axes = self.fig_time.add_subplot(111)
        self.axes.set_facecolor('white')
        self.axes.set_ylabel(self.df_x.columns[0])
        self.axes.set_xlabel('Time(s)')

        self.second_axes = self.axes.twinx()
        self.second_axes.set_ylabel(self.df_y.columns[0])


        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)
        pylab.setp(self.second_axes.get_yticklabels(), fontsize=8)

        self.ymin = int(round(self.df_x[self.df_x.columns[0]][-1], 0) - self.info['x_mag'])
        self.ymax = int(round(self.df_x[self.df_x.columns[0]][-1], 0) + self.info['x_mag'])
        self.ymin2 = int(round(self.df_y[self.df_y.columns[0]][-1], 0) - self.info['y_mag'])
        self.ymax2 = int(round(self.df_y[self.df_y.columns[0]][-1], 0) + self.info['y_mag'])


        self.plot_data = self.axes.plot(
            self.df_x.values,
            self.info['fmt']['x'],
            linewidth=1,
            color='blue',
            label=self.df_x.columns[0],
        )[0]
        self.axes.legend(loc=3)
        self.plot_data2 = self.second_axes.plot(
            self.df_y.values,
            self.info['fmt']['y'],
            linewidth=1,
            color='red',
            label=self.df_y.columns[0],
        )[0]
        self.second_axes.legend(loc=0)
        self.fig_time.tight_layout()

    def draw_plot(self):
        """ Redraws the plot
        """
        # Setting the xy plot and redraw

        if self.xy_plot_enable is True:
            self.xy_plot_enable = False
            if self.xy_plot_first_index is not None:
                self.xy_plot_first_index = None
        elif 'TR_2' in self.df['EVENT'][-1]:
            self.xy_plot_enable = True
            if self.xy_plot_first_index is None:
                self.xy_plot_first_index = self.df.index[-1]

        if self.xy_plot_enable is True:

            xy_df = pd.concat([self.df_x.loc[self.xy_plot_first_index:, self.df_x.columns[0]],
                               self.df_y.loc[self.xy_plot_first_index:, self.df_y.columns[0]]], axis=1)
            self.xy_df = self.xy_df.append(xy_df)
            # Using setp here is convenient, because get_xticklabels
            # returns a list over which one needs to explicitly
            # iterate, and setp already handles this.
            #
            pylab.setp(self.xy_plots[self.xy[0]][self.xy[1]].get_xticklabels(),
                       visible=self.cb_xlab.IsChecked())

            self.xy_plot_data = self.xy_plots[self.xy[0]][self.xy[1]].plot(
                    self.xy_df.values[:, 0],
                    self.xy_df.values[:, 1],
                    '^',
                    linewidth=0.1,
                    color='green',
                )[0]


        # when xmin is on auto, it "follows" xmax to produce a
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        if self.xmax_control.is_auto():
            xmax = self.x_list[-1]
        else:
            xmax = int(self.xmax_control.manual_value())

        if self.xmin_control.is_auto():
            if self.x_list[-1] - self.x_list[0] > 6.0:
                xmin = self.x_list[-1] - 6.0
            else:
                xmin = 0
        else:
            xmin = int(self.xmin_control.manual_value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        #
        # note that it's easy to change this scheme to the
        # minimal/maximal value in the current display, and not
        # the whole data set.
        #
        if self.ymin_control.is_auto():
            if int(round(float(self.df_x[self.df_x.columns[0]][-1]), 0)) < self.ymin + self.info['x_mag']:
                self.ymin = int(round(float(self.df_x[self.df_x.columns[0]][-1]), 0) - self.info['x_mag'])
        else:
            self.ymin = int(self.ymin_control.manual_value())

        if self.ymax_control.is_auto():
            if int(round(float(self.df_x[self.df_x.columns[0]][-1]), 0)) > self.ymax - self.info['x_mag']:
                self.ymax = int(round(float(self.df_x[self.df_x.columns[0]][-1]), 0) + self.info['x_mag'])
        else:
            self.ymax = int(self.ymax_control.manual_value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        #
        # note that it's easy to change this scheme to the
        # minimal/maximal value in the current display, and not
        # the whole data set.
        #
        if self.ymin2_control.is_auto():
            if int(round(float(self.df_y[self.df_y.columns[0]][-1]), 0)) < self.ymin2 + self.info['y_mag']:
                self.ymin2 = int(round(float(self.df_y[self.df_y.columns[0]][-1]), 0) - self.info['y_mag'])
        else:
            self.ymin2 = int(self.ymin2_control.manual_value())

        if self.ymax2_control.is_auto():
            if int(round(float(self.df_y[self.df_y.columns[0]][-1]), 0)) > self.ymax2 - self.info['y_mag']:
                self.ymax2 = int(round(float(self.df_y[self.df_y.columns[0]][-1]), 0) + self.info['y_mag'])
        else:
            self.ymax2 = int(self.ymax2_control.manual_value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=self.ymin, upper=self.ymax)
        self.second_axes.set_ybound(lower=self.ymin2, upper=self.ymax2)

        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly
        # iterate, and setp already handles this.
        #
        pylab.setp(self.axes.get_xticklabels(),
                   visible=self.cb_xlab.IsChecked())

        self.plot_data.set_xdata(np.array(self.x_list))
        self.plot_data.set_ydata(self.df_x.values)

        self.plot_data2.set_xdata(np.array(self.x_list))
        self.plot_data2.set_ydata(self.df_y.values)

        self.canvas_xy.draw()
        self.canvas_time.draw()

    def on_grid(self, x):
        x.grid(True, color='gray')

    def off_grid(self, x):
        x.grid(False)

    def on_pause_button(self, event):
        self.paused = not self.paused

    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)

    def on_cb_grid(self, event):
        self.draw_plot()

    def on_cb_xlab(self, event):
        self.draw_plot()

    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"

        dlg = wx.FileDialog(
            self,
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)

    def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        if not self.paused and self.rtp_conn.poll():
            self.data_read()

        self.draw_plot()

    def on_exit(self, event):
        self.Destroy()

    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER,
            self.on_flash_status_off,
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)

    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')


def alignToBottomRight(win):
    dw, dh = wx.DisplaySize()
    w, h = win.GetSize()
    x = dw - w
    y = dh - h
    win.SetPosition((x, y))


def RealTimePlottingDialog(rtp_conn):
    app = wx.App()
    app.frame = GraphFrame(rtp_conn)
    alignToBottomRight(app.frame)
    app.SetTopWindow(app.frame)
    app.frame.Show()
    app.MainLoop()

