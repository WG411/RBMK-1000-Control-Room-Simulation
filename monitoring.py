from __future__ import annotations
from config import *


class Monitoring:

    def tick(self):

        # apply controls

        self.sim.rod_cmd = (
            self.var_rod_cmd.get()
        )

        self.sim.flow_cmd = (
            self.var_flow.get()
        )

        self.sim.feedwater_pct = (
            self.var_feedwater.get()
        )

        self.sim.turbine_cmd = (
            self.var_turbine.get()
        )


        # physics step

        self.sim.step(DT)

        rho_pcm, margin_pcm = (
            self.sim.derived()
        )

        P_elec = (
            self.sim.electrical_output()
        )

        self.var_rod_pos.set(
            self.sim.rod_pct
        )

        self.rod_depth_pos.set(
            (
                self.sim.rod_pct
                * ROD_DEPTH
                / 100
            )
        )


        # update readouts

        self.labels[
            "Core Power (MWth)"
        ].config(
            text=f"{self.sim.P:.0f}"
        )

        self.labels[
            "Electrical Output (MWe)"
        ].config(
            text=f"{P_elec:.0f}"
        )

        self.labels[
            "Reactivity (pcm)"
        ].config(
            text=f"{rho_pcm:+.0f}"
        )

        self.labels[
            "Margin est. (pcm)"
        ].config(
            text=f"{margin_pcm:.0f}"
        )

        self.labels[
            "Fuel temp (°C)"
        ].config(
            text=f"{self.sim.T_fuel:.1f}"
        )

        self.labels[
            "Outlet temp (°C)"
        ].config(
            text=f"{self.sim.T_out:.1f}"
        )

        self.labels[
            "Pressure (MPa)"
        ].config(
            text=f"{self.sim.P_mpa:.3f}"
        )

        self.labels[
            "Coolant flow (%)"
        ].config(
            text=f"{self.sim.flow_pct:.1f}"
        )

        self.labels[
            "Feedwater flow (%)"
        ].config(
            text=f"{self.sim.feedwater_pct:.1f}"
        )

        self.labels[
            "Turbine load (%)"
        ].config(
            text=f"{self.sim.turbine_pct:.1f}"
        )

        self.labels[
            "Main Pumps"
        ].config(
            text=(
                "TRIPPED"
                if self.sim.pumps_tripped
                else "RUNNING"
            )
        )

        self.labels[
            "Turbine Status"
        ].config(
            text=(
                "TRIPPED"
                if self.sim.turbine_tripped
                else "RUNNING"
            )
        )

        self.labels[
            "Steam Dump"
        ].config(
            text=(
                "OPEN"
                if self.sim.steam_dump_open
                else "CLOSED"
            )
        )

        self.labels[
            "Time (s)"
        ].config(
            text=f"{self.sim._t:.2f}"
        )

        self.labels[
            "Rod Position Target (%)"
        ].config(
            text=f"{self.var_rod_cmd.get():.2f}"
        )

        self.labels[
            "Rod Position Current (%)"
        ].config(
            text=f"{self.sim.rod_pct:.2f}"
        )


        # alarms

        alarms = []


        if self.sim.scram:

            alarms.append(
                "SCRAM"
            )


        if (
            CRITICALLY_HIGH
            >= self.sim.P
            >= MAXIMUM_POWER_LVL
        ):

            if self.sim.rod_pct == 100:

                alarms.append(
                    "HIGH POWER"
                )

            else:

                alarms.append(
                    "HIGH POWER, INSERT RODS"
                )


        if self.sim.P >= CRITICALLY_HIGH:

            if self.sim.scram:

                alarms.append(
                    "EMERGENCY PRECAUTIONS"
                )

            else:

                alarms.append(
                    "ACTIVATE AZ-5"
                )


        if (
            CRITICALLY_LOW
            <= self.sim.P
            <= MINIMUM_POWER_LVL
        ):

            if self.sim.scram:

                alarms.append(
                    "REACTOR TRIPPED (AZ-5)"
                )

            else:

                alarms.append(
                    "LOW POWER"
                )


        if self.sim.P <= CRITICALLY_LOW:

            if self.sim.scram:

                alarms.append(
                    "AZ-5 ENGAGED — CORE SUBCRITICAL"
                )

            elif self.sim.rod_pct == 0:

                alarms.append(
                    "CRITICALLY LOW POWER"
                )

            else:

                alarms.append(
                    "CRITICALLY LOW POWER, FULLY WITHDRAW RODS"
                )


        if self.sim.T_out >= OUTLET_T_HIGH:

            alarms.append(
                "HIGH OUTLET T"
            )


        if margin_pcm <= LOW_MARGIN_PCM:

            alarms.append(
                "LOW MARGIN"
            )


        if (
            self.sim.P_mpa
            >= PRESSURE_HIGH_MPA
        ):

            alarms.append(
                "HIGH PRESSURE"
            )


        if (
            self.sim.P_mpa
            <= PRESSURE_LOW_MPA
        ):

            alarms.append(
                "LOW PRESSURE"
            )


        if (
            self.sim.flow_pct
            <= LOW_COOLANT_FLOW_PCT
        ):

            alarms.append(
                "LOW COOLANT FLOW"
            )


        if (
            self.sim.feedwater_pct
            <= LOW_FEEDWATER_PCT
        ):

            alarms.append(
                "LOW FEEDWATER"
            )


        if self.sim.pumps_tripped:

            alarms.append(
                "MAIN PUMPS TRIPPED"
            )


        if self.sim.turbine_tripped:

            alarms.append(
                "TURBINE TRIP"
            )


        self.status.set(
            " | ".join(alarms)
            if alarms
            else "Normal"
        )


        self.root.after(
            int(DT * 1000),
            self.tick
        )

