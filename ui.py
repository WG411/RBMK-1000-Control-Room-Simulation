from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from reactor_model import Sim
from control_logic import ControlLogic
from monitoring import Monitoring


class App(ControlLogic, Monitoring):

    def __init__(self, root: tk.Tk):

        self.root = root

        self.hold_status = tk.StringVar(
            self.root,
            value="Disabled"
        )

        self.ph_status = tk.StringVar(
            self.root,
            value="N/A"
        )

        self.action_status = tk.StringVar(
            self.root,
            value=""
        )

        root.title(
            "RBMK-1000 Control Room Simulation"
        )

        self.P_target = None

        self.sim = Sim()

        self.reset_sliders = Sim()

        self.autothrottle_job = None

        self.autothrottle_enabled = False


        # layout

        self.left = ttk.LabelFrame(
            root,
            text="Controls"
        )

        self.right = ttk.LabelFrame(
            root,
            text="Readouts"
        )

        self.bottom = ttk.LabelFrame(
            root,
            text="Status / Actions"
        )

        self.leftbot = ttk.LabelFrame(
            root,
            text="Rod controls"
        )

        self.middle = ttk.LabelFrame(
            root,
            text="Rod Control"
        )

        self.rightbot = ttk.LabelFrame(
            root,
            text="Simulator"
        )

        self.left.grid(
            row=0,
            column=0,
            padx=8,
            pady=8,
            sticky="nsew"
        )

        self.leftbot.grid(
            row=1,
            column=0,
            padx=8,
            pady=8,
            sticky="nsew"
        )

        self.right.grid(
            row=0,
            column=2,
            padx=8,
            pady=8,
            sticky="nsew"
        )

        self.bottom.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=8,
            pady=(0, 8),
            sticky="ew"
        )

        self.middle.grid(
            row=0,
            column=1,
            padx=8,
            pady=8,
            sticky="nsew"
        )

        self.rightbot.grid(
            row=2,
            column=2,
            padx=8,
            pady=8,
            sticky="nsew"
        )


        # rod controls

        p = ttk.Frame(
            self.leftbot
        )

        p.grid(
            row=1,
            column=0,
            columnspan=1,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            p,
            text="Rod Control:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 6)
        )


        ph_read = ttk.Frame(
            self.leftbot
        )

        ph_read.grid(
            row=3,
            column=1,
            columnspan=1,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            ph_read,
            text="Power Hold Target (MWth):"
        ).grid(
            row=0,
            column=0,
            padx=(0, 6)
        )


        j = ttk.Frame(
            self.leftbot
        )

        j.grid(
            row=1,
            column=1,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            j,
            text="Jog:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 6)
        )


        apjog = ttk.Frame(
            self.leftbot
        )

        apjog.grid(
            row=2,
            column=1,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            apjog,
            text="Jog:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 6)
        )


        az5 = ttk.Frame(
            self.leftbot
        )

        az5.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            az5,
            text="EMER:           "
        ).grid(
            row=2,
            column=0,
            padx=(0, 9)
        )


        ap = ttk.Frame(
            self.leftbot
        )

        ap.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            ap,
            text="Power Hold:"
        ).grid(
            row=2,
            column=0,
            padx=(0, 8)
        )

        ttk.Button(
            ap,
            text="Power Hold",
            width=20,
            command=self.powerhold
        ).grid(
            row=2,
            column=1,
            padx=2
        )

        ttk.Button(
            ap,
            text="Disable Power Hold",
            width=20,
            command=self.stop_powerhold
        ).grid(
            row=2,
            column=2,
            padx=2
        )


        for col, delta in enumerate(
            [-50, -10, -1, +1, +10, +50],
            start=1
        ):

            ttk.Button(
                apjog,
                text=f"{delta:+d}",
                width=4,
                command=lambda d=delta: self.pjog(d)
            ).grid(
                row=0,
                column=col,
                padx=2
            )


        apstatus = ttk.Frame(
            self.leftbot
        )

        apstatus.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            apstatus,
            text="Power Hold:"
        ).grid(
            row=2,
            column=0,
            padx=(0, 8)
        )

        ttk.Label(
            apstatus,
            textvariable=self.hold_status
        ).grid(
            row=2,
            column=1,
            padx=(0, 8)
        )

        ttk.Label(
            ph_read,
            textvariable=self.ph_status
        ).grid(
            row=0,
            column=1,
            padx=(0, 8)
        )


        # simulator

        co = ttk.Frame(
            self.rightbot
        )

        co.grid(
            row=4,
            column=2,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Button(
            co,
            text="Reset",
            width=20,
            command=self.reset_sim
        ).grid(
            row=1,
            column=0,
            padx=2
        )

        ttk.Button(
            co,
            text="Restart",
            width=20,
            command=self.restart_sim
        ).grid(
            row=1,
            column=1,
            padx=2
        )

        ttk.Button(
            co,
            text="Reset SCRAM",
            width=20,
            command=self.reset_scram
        ).grid(
            row=2,
            column=0,
            padx=2,
            pady=(4, 0)
        )

        ttk.Label(
            co,
            textvariable=self.action_status
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(4, 0)
        )


        # rod control display

        rc = ttk.Frame(
            self.middle
        )

        rc.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(1, 0)
        )

        self.var_rod = tk.DoubleVar(
            value=self.sim.rod_pct
        )

        self.var_rod_pos = tk.DoubleVar(
            value=self.sim.rod_pct
        )

        self.var_rod_cmd = tk.DoubleVar(
            value=self.sim.rod_pct
        )

        self.rod_depth_pos = tk.DoubleVar(
            value=self.sim.rod_pct
        )

        self._progressbar(
            rc,
            "Rod position (0-100%)  ",
            "horizontal",
            "determinate",
            750,
            100,
            self.var_rod_pos,
            row=2
        )

        self._progressbar(
            rc,
            "Rod Depth (m) ",
            "horizontal",
            "determinate",
            750,
            7,
            self.rod_depth_pos,
            row=3
        )


        ttk.Button(
            p,
            text="Insert Rod 0.1%",
            width=20,
            command=self.rodInsert
        ).grid(
            row=0,
            column=2,
            padx=2
        )

        ttk.Button(
            p,
            text="Withdraw Rod 0.1%",
            width=20,
            command=self.rodWithdraw
        ).grid(
            row=0,
            column=1,
            padx=2
        )

        root.columnconfigure(
            0,
            weight=1
        )

        root.columnconfigure(
            1,
            weight=1
        )

        root.rowconfigure(
            0,
            weight=1
        )

        ttk.Button(
            az5,
            text="АZ-5",
            width=100,
            command=self.do_scram
        ).grid(
            row=2,
            column=1,
            padx=0
        )


        for col, delta in enumerate(
            [-10, -3, -1, +1, +3, +10],
            start=1
        ):

            ttk.Button(
                j,
                text=f"{delta:+d}",
                width=4,
                command=lambda d=delta: self.jog(d)
            ).grid(
                row=0,
                column=col,
                padx=2
            )


        # control vars

        self.var_flow = tk.DoubleVar(
            value=self.sim.flow_pct
        )

        self.var_feedwater = tk.DoubleVar(
            value=self.sim.feedwater_pct
        )

        self.var_turbine = tk.DoubleVar(
            value=self.sim.turbine_pct
        )


        # controls

        self._slider(
            self.left,
            "Coolant flow (%)",
            self.var_flow,
            0,
            100,
            1
        )

        self._slider(
            self.left,
            "Feedwater flow (%)",
            self.var_feedwater,
            0,
            100,
            2
        )

        self._slider(
            self.left,
            "Turbine load (%)",
            self.var_turbine,
            0,
            100,
            3
        )


        # pump controls

        pumpcontrols = ttk.Frame(
            self.left
        )

        pumpcontrols.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            pumpcontrols,
            text="Pumps:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 6)
        )

        ttk.Button(
            pumpcontrols,
            text="Trip Pumps",
            width=15,
            command=self.trip_pumps
        ).grid(
            row=0,
            column=1,
            padx=2
        )

        ttk.Button(
            pumpcontrols,
            text="Restore Pumps",
            width=15,
            command=self.restore_pumps
        ).grid(
            row=0,
            column=2,
            padx=2
        )


        # turbine controls

        turbinecontrols = ttk.Frame(
            self.left
        )

        turbinecontrols.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            turbinecontrols,
            text="Turbine:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 6)
        )

        ttk.Button(
            turbinecontrols,
            text="Trip Turbine",
            width=15,
            command=self.trip_turbine
        ).grid(
            row=0,
            column=1,
            padx=2
        )

        ttk.Button(
            turbinecontrols,
            text="Reset Turbine",
            width=15,
            command=self.reset_turbine
        ).grid(
            row=0,
            column=2,
            padx=2
        )


        # steam dump

        dumpcontrols = ttk.Frame(
            self.left
        )

        dumpcontrols.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            dumpcontrols,
            text="Steam Dump:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 6)
        )

        ttk.Button(
            dumpcontrols,
            text="Open",
            width=15,
            command=self.open_steam_dump
        ).grid(
            row=0,
            column=1,
            padx=2
        )

        ttk.Button(
            dumpcontrols,
            text="Close",
            width=15,
            command=self.close_steam_dump
        ).grid(
            row=0,
            column=2,
            padx=2
        )


        # readouts

        self.labels = {}

        self._ro(
            "Core Power (MWth)",
            0
        )

        self._ro(
            "Electrical Output (MWe)",
            1
        )

        self._ro(
            "Reactivity (pcm)",
            2
        )

        self._ro(
            "Margin est. (pcm)",
            3
        )

        self._ro(
            "Fuel temp (°C)",
            4
        )

        self._ro(
            "Outlet temp (°C)",
            5
        )

        self._ro(
            "Pressure (MPa)",
            6
        )

        self._ro(
            "Coolant flow (%)",
            7
        )

        self._ro(
            "Feedwater flow (%)",
            8
        )

        self._ro(
            "Turbine load (%)",
            9
        )

        self._ro(
            "Main Pumps",
            10
        )

        self._ro(
            "Turbine Status",
            11
        )

        self._ro(
            "Steam Dump",
            12
        )

        self._ro(
            "Time (s)",
            13
        )

        self._rc(
            "Rod Position Target (%)",
            0
        )

        self._rc(
            "Rod Position Current (%)",
            1
        )


        # status

        self.status = tk.StringVar(
            value="Ready"
        )

        self.reset_status = tk.StringVar(
            value="Reset"
        )

        ttk.Label(
            self.bottom,
            textvariable=self.status
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )


        # start loop

        self.tick()


    def _slider(
        self,
        parent,
        text,
        var,
        lo,
        hi,
        row
    ):

        ttk.Label(
            parent,
            text=text
        ).grid(
            row=row,
            column=0,
            sticky="w"
        )

        s = ttk.Scale(
            parent,
            variable=var,
            from_=lo,
            to=hi,
            orient="horizontal"
        )

        s.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(8, 0)
        )

        parent.columnconfigure(
            1,
            weight=1
        )


    def _progressbar(
        self,
        parent,
        text,
        orient,
        mode,
        le,
        max,
        var,
        row
    ):

        ttk.Label(
            parent,
            text=text
        ).grid(
            row=row,
            column=0,
            sticky="w"
        )

        w = ttk.Progressbar(
            parent,
            orient=orient,
            mode=mode,
            length=le,
            maximum=max,
            variable=var
        )

        w.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(8, 0)
        )

        parent.columnconfigure(
            1,
            weight=1
        )

        return w


    def _ro(self, name, row):

        ttk.Label(
            self.right,
            text=name
        ).grid(
            row=row,
            column=0,
            sticky="w"
        )

        val = ttk.Label(
            self.right,
            text="-"
        )

        val.grid(
            row=row,
            column=1,
            sticky="e"
        )

        self.labels[name] = val


    def _rc(self, name, row):

        ttk.Label(
            self.middle,
            text=name
        ).grid(
            row=row,
            column=0,
            sticky="w"
        )

        val1 = ttk.Label(
            self.middle,
            text="-"
        )

        val1.grid(
            row=row,
            column=1,
            sticky="e"
        )

        self.labels[name] = val1

