class ConcentrationCalculator:
    _CONTRACTION_TABLE = [
        (10, 0.8),
        (20, 1.5),
        (30, 2.2),
        (40, 2.7),
        (50, 3.2),
        (60, 3.1),
        (70, 2.5),
        (80, 1.7),
        (90, 1.0),
    ]

    @staticmethod
    def _get_contraction_rate(abv, temperature=20.0):
        if abv <= 0 or abv >= 100:
            return 0.0

        if abv <= ConcentrationCalculator._CONTRACTION_TABLE[0][0]:
            rate = ConcentrationCalculator._CONTRACTION_TABLE[0][1] * (abv / ConcentrationCalculator._CONTRACTION_TABLE[0][0])
        elif abv >= ConcentrationCalculator._CONTRACTION_TABLE[-1][0]:
            rate = ConcentrationCalculator._CONTRACTION_TABLE[-1][1]
        else:
            for i in range(len(ConcentrationCalculator._CONTRACTION_TABLE) - 1):
                abv1, rate1 = ConcentrationCalculator._CONTRACTION_TABLE[i]
                abv2, rate2 = ConcentrationCalculator._CONTRACTION_TABLE[i + 1]
                if abv1 <= abv <= abv2:
                    rate = rate1 + (rate2 - rate1) * (abv - abv1) / (abv2 - abv1)
                    break

        if temperature != 20.0:
            rate = rate * (1 + 0.00065 * (temperature - 20.0))

        return max(0.0, rate)

    @staticmethod
    def calculate_solvent_volume(mother_concentration, target_concentration, mother_volume,
                                 correct_contraction=False, temperature=20.0,
                                 manual_contraction_rate=None):
        if mother_concentration <= 0:
            raise ValueError("母液浓度必须大于0")
        if mother_concentration > 100:
            raise ValueError("母液浓度不能超过100%")
        if target_concentration <= 0:
            raise ValueError("目标浓度必须大于0")
        if target_concentration > 100:
            raise ValueError("目标浓度不能超过100%")
        if mother_volume <= 0:
            raise ValueError("母液体积必须大于0")
        if target_concentration >= mother_concentration:
            raise ValueError("目标浓度必须小于母液浓度（稀释操作）")

        theoretical_solvent = mother_volume * (mother_concentration - target_concentration) / target_concentration
        theoretical_final = mother_volume + theoretical_solvent

        if not correct_contraction:
            return {
                "solvent_volume": round(theoretical_solvent, 4),
                "final_volume": round(theoretical_final, 4),
                "dilution_factor": round(mother_concentration / target_concentration, 4),
                "contraction_corrected": False
            }

        if manual_contraction_rate is not None:
            if manual_contraction_rate < 0 or manual_contraction_rate > 10:
                raise ValueError("手动收缩率应在0-10%范围内")
            contraction_rate = manual_contraction_rate
        else:
            contraction_rate = ConcentrationCalculator._get_contraction_rate(target_concentration, temperature)

        contraction_factor = 1 - (contraction_rate / 100.0)
        corrected_final = theoretical_final / contraction_factor
        corrected_solvent = corrected_final - mother_volume
        volume_difference = corrected_solvent - theoretical_solvent

        return {
            "solvent_volume": round(theoretical_solvent, 4),
            "corrected_solvent_volume": round(corrected_solvent, 4),
            "final_volume": round(theoretical_final, 4),
            "corrected_final_volume": round(corrected_final, 4),
            "dilution_factor": round(mother_concentration / target_concentration, 4),
            "contraction_corrected": True,
            "contraction_rate": round(contraction_rate, 4),
            "volume_difference": round(volume_difference, 4),
            "temperature": temperature
        }

    @staticmethod
    def volume_to_mass_concentration(volume_percent, solute_density, solution_density):
        if volume_percent < 0 or volume_percent > 100:
            raise ValueError("体积百分比浓度应在0-100%范围内")
        if solute_density <= 0:
            raise ValueError("溶质密度必须大于0")
        if solution_density <= 0:
            raise ValueError("溶液密度必须大于0")

        mass_percent = (volume_percent * solute_density) / solution_density
        mass_volume = (volume_percent / 100.0) * solute_density * 1000.0

        return {
            "volume_percent": round(volume_percent, 4),
            "mass_percent": round(mass_percent, 4),
            "mass_volume_g_per_L": round(mass_volume, 4),
            "mass_volume_mg_per_mL": round(mass_volume, 4),
            "solute_density": solute_density,
            "solution_density": solution_density
        }

    @staticmethod
    def mass_to_volume_concentration(mass_percent, solute_density, solution_density):
        if mass_percent < 0 or mass_percent > 100:
            raise ValueError("质量百分比浓度应在0-100%范围内")
        if solute_density <= 0:
            raise ValueError("溶质密度必须大于0")
        if solution_density <= 0:
            raise ValueError("溶液密度必须大于0")

        volume_percent = (mass_percent * solution_density) / solute_density
        mass_volume = (mass_percent / 100.0) * solution_density * 1000.0

        return {
            "mass_percent": round(mass_percent, 4),
            "volume_percent": round(volume_percent, 4),
            "mass_volume_g_per_L": round(mass_volume, 4),
            "mass_volume_mg_per_mL": round(mass_volume, 4),
            "solute_density": solute_density,
            "solution_density": solution_density
        }

    @staticmethod
    def mass_volume_conversion(concentration_value, from_unit, to_unit,
                               solution_density=None, molar_mass=None):
        valid_units = [
            "g/L", "g/dL", "mg/mL", "mg/dL", "μg/mL", "μg/L", "ng/mL", "pg/mL",
            "mol/L", "mmol/L", "μmol/L", "nmol/L", "pmol/L",
            "w/w%", "w/v%", "v/v%",
            "ppm", "ppb"
        ]
        if from_unit not in valid_units:
            raise ValueError(f"不支持的源单位: {from_unit}。支持: {', '.join(valid_units)}")
        if to_unit not in valid_units:
            raise ValueError(f"不支持的目标单位: {to_unit}。支持: {', '.join(valid_units)}")

        molar_units = ["mol/L", "mmol/L", "μmol/L"]
        if (from_unit in molar_units or to_unit in molar_units) and molar_mass is None:
            raise ValueError("进行摩尔浓度转换时必须提供 molar_mass (g/mol)")

        ww_units = ["w/w%"]
        if (from_unit in ww_units or to_unit in ww_units) and solution_density is None:
            raise ValueError("进行质量百分比转换时必须提供 solution_density (g/mL)")

        wv_units = ["w/v%"]
        if (from_unit in wv_units or to_unit in wv_units) and solution_density is None:
            if from_unit == "w/v%" or to_unit == "w/v%":
                pass

        g_per_L_value = ConcentrationCalculator._to_g_per_L(
            concentration_value, from_unit, solution_density, molar_mass
        )

        result_value = ConcentrationCalculator._from_g_per_L(
            g_per_L_value, to_unit, solution_density, molar_mass
        )

        return {
            "input": {
                "value": concentration_value,
                "unit": from_unit
            },
            "output": {
                "value": round(result_value, 6),
                "unit": to_unit
            },
            "g_per_L_equivalent": round(g_per_L_value, 6),
            "conversion_factor": round(result_value / concentration_value, 6) if concentration_value != 0 else 0
        }

    @staticmethod
    def _to_g_per_L(value, unit, solution_density, molar_mass):
        if unit == "g/L":
            return value
        elif unit == "g/dL":
            return value * 10.0
        elif unit == "mg/mL":
            return value * 1.0
        elif unit == "mg/dL":
            return value / 100.0
        elif unit == "μg/mL":
            return value / 1000.0
        elif unit == "μg/L":
            return value / 1_000_000.0
        elif unit == "ng/mL":
            return value / 1_000_000.0
        elif unit == "pg/mL":
            return value / 1_000_000_000.0
        elif unit == "mol/L":
            return value * molar_mass
        elif unit == "mmol/L":
            return value * molar_mass / 1000.0
        elif unit == "μmol/L":
            return value * molar_mass / 1_000_000.0
        elif unit == "nmol/L":
            return value * molar_mass / 1_000_000_000.0
        elif unit == "pmol/L":
            return value * molar_mass / 1_000_000_000_000.0
        elif unit == "w/w%":
            return (value / 100.0) * solution_density * 1000.0
        elif unit == "w/v%":
            return value * 10.0
        elif unit == "v/v%":
            return (value / 100.0) * solution_density * 1000.0
        elif unit == "ppm":
            return value / 1000.0
        elif unit == "ppb":
            return value / 1_000_000.0
        return value

    @staticmethod
    def _from_g_per_L(g_per_L, unit, solution_density, molar_mass):
        if unit == "g/L":
            return g_per_L
        elif unit == "g/dL":
            return g_per_L / 10.0
        elif unit == "mg/mL":
            return g_per_L / 1.0
        elif unit == "mg/dL":
            return g_per_L * 100.0
        elif unit == "μg/mL":
            return g_per_L * 1000.0
        elif unit == "μg/L":
            return g_per_L * 1_000_000.0
        elif unit == "ng/mL":
            return g_per_L * 1_000_000.0
        elif unit == "pg/mL":
            return g_per_L * 1_000_000_000.0
        elif unit == "mol/L":
            return g_per_L / molar_mass
        elif unit == "mmol/L":
            return g_per_L * 1000.0 / molar_mass
        elif unit == "μmol/L":
            return g_per_L * 1_000_000.0 / molar_mass
        elif unit == "nmol/L":
            return g_per_L * 1_000_000_000.0 / molar_mass
        elif unit == "pmol/L":
            return g_per_L * 1_000_000_000_000.0 / molar_mass
        elif unit == "w/w%":
            return (g_per_L / (solution_density * 1000.0)) * 100.0
        elif unit == "w/v%":
            return g_per_L / 10.0
        elif unit == "v/v%":
            return (g_per_L / (solution_density * 1000.0)) * 100.0
        elif unit == "ppm":
            return g_per_L * 1000.0
        elif unit == "ppb":
            return g_per_L * 1_000_000.0
        return g_per_L
