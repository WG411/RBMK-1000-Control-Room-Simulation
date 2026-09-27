from __future__ import annotations
import tkinter as tk
import os, sys

from config import *
from reactor_model import Sim


class ControlLogic:

    def restart_sim(self):

        python = sys.executable

        os.execl(
            python,
            python,
            *sys.argv
        )


    def reset_sim(self):

        self.stop_powerhold()

        self.sim.reset()

        self.P_target = None

        self.var_rod.set(
            self.sim.rod_pct
        )

        self.var_flow.set(
            self.sim.flow_pct
        )

        self.var_feedwater.set(
            self.sim.feedwater_pct
        )

        self.var_turbine.set(
            self.sim.turbine_pct
        )

        self.var_rod_pos.set(
            self.sim.rod_pct
        )

        self.var_rod_cmd.set(
            self.sim.rod_pct
        )

        self.status.set(
            "Reset"
        )

        self.action_status.set(
            "Simulator reset"
        )

        self.reset_sliders = Sim()


    def jog(self, delta_pp):

        new_cmd = max(
            0.0,
            min(
                100.0,
                self.var_rod_cmd.get()
                + float(delta_pp)
            )
        )

        self.var_rod_cmd.set(
            new_cmd
        )


    def pjog(self, delta_ph):

        if self.autothrottle_enabled == True:

            TARGET = float(
                delta_ph
            )

            self.P_target += TARGET

        else:
            pass


    def powerhold(self):

        if not self.autothrottle_enabled:

            self.P_target = float(
                self.sim.P
            )

            self.hold_status.set(
                "Enabled"
            )

            self.autothrottle_enabled = True

            self.autothrottle()


    def stepUpPower(self):

        TARGETINC = 10

        self.P_target += TARGETINC


    def stepDownPower(self):

        TARGETINC = 10

        self.P_target -= TARGETINC


    def autothrottle(self):

        if not self.autothrottle_enabled:
            return

        P = self.sim.P

        target = float(
            self.P_target
        )

        self.ph_status.set(
            f"{self.P_target:.0f}"
        )

        banderr = 1

        err = target - P

        if err > banderr:

            if err > 200:
                step = 0.12

            elif err > 50:
                step = 0.02

            elif err > 5:
                step = 0.002

            else:
                step = 0.0005

            self.var_rod_cmd.set(
                max(
                    0.0,
                    self.var_rod_cmd.get()
                    - step
                )
            )

        elif err < -banderr:

            if -err > 200:
                step = 0.12

            elif -err > 50:
                step = 0.02

            elif -err > 5:
                step = 0.002

            else:
                step = 0.0005

            self.var_rod_cmd.set(
                min(
                    100.0,
                    self.var_rod_cmd.get()
                    + step
                )
            )

        self.autothrottle_job = (
            self.root.after(
                int(
                    DT
                    * 0.1
                    * 1000
                ),
                self.autothrottle
            )
        )


    def stop_powerhold(self):

        self.autothrottle_enabled = False

        self.P_target = None

        if self.autothrottle_job is not None:

            try:

                self.root.after_cancel(
                    self.autothrottle_job
                )

            except tk.TclError:
                pass

            self.autothrottle_job = None

        self.hold_status.set(
            "Disabled"
        )

        self.ph_status.set(
            "N/A"
        )


    def rodInsert(self):

        self.var_rod_cmd.set(
            min(
                100.0,
                self.var_rod_cmd.get()
                + 0.1
            )
        )


    def rodWithdraw(self):

        self.var_rod_cmd.set(
            max(
                0,
                self.var_rod_cmd.get()
                - 0.1
            )
        )


    def trip_pumps(self):

        self.sim.pumps_tripped = True

        self.action_status.set(
            "Main circulation pumps tripped"
        )


    def restore_pumps(self):

        self.sim.pumps_tripped = False

        self.action_status.set(
            "Main circulation pumps restored"
        )


    def trip_turbine(self):

        self.sim.turbine_tripped = True

        self.action_status.set(
            "Turbine tripped"
        )


    def reset_turbine(self):

        self.sim.turbine_tripped = False

        self.action_status.set(
            "Turbine reset"
        )


    def open_steam_dump(self):

        self.sim.steam_dump_open = True

        self.action_status.set(
            "Steam dump opened"
        )


    def close_steam_dump(self):

        self.sim.steam_dump_open = False

        self.action_status.set(
            "Steam dump closed"
        )


    def reset_scram(self):

        if not self.sim.scram:

            self.action_status.set(
                "SCRAM is not active"
            )

            return

        if (
            self.sim.P >= 50.0
            or self.sim.rod_pct < 95.0
        ):

            self.action_status.set(
                "SCRAM reset blocked"
            )

            return

        self.sim.scram = False

        self.action_status.set(
            "SCRAM reset"
        )


    def do_scram(self):

        self.sim.scram = True

        self.status.set(
            "SCRAM pressed"
        )

        self.var_rod_cmd.set(
            100
        )

        self.stop_powerhold()

