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
