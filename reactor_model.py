from __future__ import annotations
from config import *

class Sim:

    @staticmethod
    def _slew(current, target, rate_per_s, dt):

        delta = rate_per_s * dt

        if target > current:
            return min(target, current + delta)

        if target < current:
            return max(target, current - delta)

        return current


    def reset(self):

        self.P = 3300
        self.T_fuel = 500.0
        self.T_in = NOMINAL_INLET_C
        self.T_out = 290.0
        self.P_mpa = NOMINAL_PRESSURE_MPA

        self.scram = False

        # controls
        self.rod_pct = 14
        self.flow_pct = 80.0
        self.hold_power_mwth = None

        self.feedwater_pct = 100.0
        self.turbine_pct = 100.0

        # system states
        self.pumps_tripped = False
        self.turbine_tripped = False
        self.steam_dump_open = False

        # internal
        self._t = 0.0
        self._step_i = 0

        self.C = (
            BETA_EFF
            / (ULAMBDA * LLAMBDA)
        ) * self.P

        self.rod_cmd = self.rod_pct
        self.flow_cmd = self.flow_pct
        self.turbine_cmd = self.turbine_pct


    def __init__(self):

        self.P = 3200
        self.T_fuel = 500.0
        self.T_in = NOMINAL_INLET_C
        self.T_out = 290.0
        self.P_mpa = NOMINAL_PRESSURE_MPA

        self.scram = False

        # controls
        self.rod_pct = 14
        self.flow_pct = 80.0
        self.hold_power_mwth = None

        self.feedwater_pct = 100.0
        self.turbine_pct = 100.0

        # system states
        self.pumps_tripped = False
        self.turbine_tripped = False
        self.steam_dump_open = False

        # internal
        self._t = 0.0
        self._step_i = 0

        self.C = (
            BETA_EFF
            / (ULAMBDA * LLAMBDA)
        ) * self.P

        self.rod_cmd = self.rod_pct
        self.flow_cmd = self.flow_pct
        self.turbine_cmd = self.turbine_pct


    @staticmethod
    def clamp(x, lo, hi):

        return lo if x < lo else hi if x > hi else x


    def flow_rel(self):

        rel = (
            FLOW_MIN
            + (FLOW_MAX - FLOW_MIN)
            * (self.flow_pct / 100.0)
        )

        return self.clamp(
            rel,
            0.4,
            2.0
        )


    def rho_eff(self):

        # rods
        rho_rod_pcm = (
            self.rod_pct / 100
        ) * ROD_WORTH_PCM_AT_100

        # fuel temperature feedback
        rho_T_pcm = (
            ALPHA_T_FUEL_PCM_PER_C
            * (
                self.T_fuel
                - FUEL_REACTIVITY_REF_C
            )
        )

        # void
        effective_void_ref_C = (
            VOID_REF_OUTLET_C
            + VOID_PRESSURE_SHIFT_C_PER_MPA
            * (
                self.P_mpa
                - NOMINAL_PRESSURE_MPA
            )
        )

        void_drive = (
            self.T_out
            - effective_void_ref_C
        ) * VOID_SLOPE_PER_C

        void = self.clamp(
            void_drive
            / max(
                0.4,
                self.flow_rel()
            ),
            0.0,
            1.0
        )

        rho_void_pcm = (
            ALPHA_VOID_PCM_PER_FRAC
            * void
        )

        # scram
        rho_scram_pcm = (
            SCRAM_RHO_PCM
            if self.scram
            else 0.0
        )

        # sum in pcm
        rho_pcm = (
            CORE_EXCESS_REACTIVITY_PCM
            + rho_rod_pcm
            + rho_T_pcm
            + rho_void_pcm
            + rho_scram_pcm
        )

        rho_pcm = self.clamp(
            rho_pcm,
            -MAX_RHO_ABS / PCM,
            MAX_RHO_ABS / PCM
        )

        return rho_pcm * PCM


    def electrical_output(self):

        turbine_fraction = self.clamp(
            self.turbine_pct / 100.0,
            0.0,
            1.0
        )

        if self.steam_dump_open:

            turbine_fraction *= (
                1.0
                - STEAM_DUMP_ELECTRICAL_PENALTY
            )

        return (
            self.P
            * EFFICIENCY
            * turbine_fraction
        )


    def step(self, dt: float):

        if self.scram == True:
            K = 20

        else:
            K = 10

        # rod actuator
        self.rod_pct = self._slew(
            self.rod_pct,
            self.rod_cmd,
            K,
            dt
        )

        # coolant pumps
        if self.pumps_tripped:

            flow_target = PUMP_TRIP_FLOW_PCT

        else:

            flow_target = self.flow_cmd

        self.flow_pct = self._slew(
            self.flow_pct,
            flow_target,
            10.0,
            dt
        )

        # turbine
        if self.turbine_tripped:

            turbine_target = 0.0

        else:

            turbine_target = self.turbine_cmd

        self.turbine_pct = self._slew(
            self.turbine_pct,
            turbine_target,
            TURBINE_SLEW_PCT_PER_S,
            dt
        )

        # fuel temperature
        power_fraction = max(
            0.0,
            self.P / NOMINAL_POWER_MWTH
        )

        target_fuel = (
            self.T_out
            + FUEL_COOLANT_DELTA_C
            * power_fraction
        )

        self.T_fuel += (
            target_fuel
            - self.T_fuel
        ) * dt / FUEL_TAU

        # reactor kinetics
        rho = self.rho_eff()

        beta = BETA_EFF
        Λ = ULAMBDA
        λ = LLAMBDA

        den = (
            1.0
            - dt
            * (
                (rho - beta)
                / Λ
            )
        )

        if den < 1e-6:
            den = 1e-6

        P_next = (
            self.P
            + dt
            * λ
            * self.C
        ) / den

        P_next = max(
            0.0,
            P_next
        )

        C_next = (
            self.C
            + dt
            * (
                (beta / Λ)
                * P_next
                - λ
                * self.C
            )
        )

        C_next = max(
            0.0,
            C_next
        )

        self.P, self.C = (
            P_next,
            C_next
        )

        # coolant outlet temperature
        nominal_rise = (
            NOMINAL_OUTLET_C
            - NOMINAL_INLET_C
        )

        feedwater_fraction = self.clamp(
            self.feedwater_pct / 100.0,
            0.0,
            1.0
        )

        feedwater_cooling_factor = (
            FEEDWATER_MIN_COOLING_FACTOR
            + (
                1.0
                - FEEDWATER_MIN_COOLING_FACTOR
            )
            * feedwater_fraction
        )

        cooling_factor = (
            self.flow_rel()
            * feedwater_cooling_factor
        )

        rise = (
            nominal_rise
            * (
                self.P
                / NOMINAL_POWER_MWTH
            )
            / max(
                1e-6,
                cooling_factor
            )
        )

        target_out = (
            self.T_in
            + rise
        )

        self.T_out += (
            target_out
            - self.T_out
        ) * dt / COOLANT_TAU

        # pressure
        thermal_load = (
            (
                self.P
                / NOMINAL_POWER_MWTH
            )
            / max(
                0.4,
                self.flow_rel()
            )
        )

        turbine_fraction = self.clamp(
            self.turbine_pct / 100.0,
            0.0,
            1.0
        )

        if self.steam_dump_open:

            dump_relief = (
                STEAM_DUMP_PRESSURE_RELIEF_MPA
            )

        else:

            dump_relief = 0.0

        p_target = (
            NOMINAL_PRESSURE_MPA
            + PRESSURE_K
            * (
                self.T_out
                - NOMINAL_OUTLET_C
            )
            + PRESSURE_POWER_K
            * (
                thermal_load
                - 1.0
            )
            + TURBINE_UNLOAD_PRESSURE_K
            * (
                1.0
                - turbine_fraction
            )
            - dump_relief
        )

        p_target = max(
            0.1,
            p_target
        )

        self.P_mpa += (
            p_target
            - self.P_mpa
        ) * dt / PRESSURE_TAU

        self._t += dt
        self._step_i += 1


    def derived(self):

        rho_pcm = (
            self.rho_eff()
            / PCM
        )

        margin_pcm = max(
            0.0,
            (
                BETA_EFF
                / PCM
            )
            - rho_pcm
        )

        return rho_pcm, margin_pcm

