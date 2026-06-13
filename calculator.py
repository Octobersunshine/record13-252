class ConcentrationCalculator:
    @staticmethod
    def calculate_solvent_volume(mother_concentration, target_concentration, mother_volume):
        if mother_concentration <= 0:
            raise ValueError("母液浓度必须大于0")
        if target_concentration <= 0:
            raise ValueError("目标浓度必须大于0")
        if mother_volume <= 0:
            raise ValueError("母液体积必须大于0")
        if target_concentration >= mother_concentration:
            raise ValueError("目标浓度必须小于母液浓度（稀释操作）")

        solvent_volume = mother_volume * (mother_concentration - target_concentration) / target_concentration
        final_volume = mother_volume + solvent_volume

        return {
            "solvent_volume": round(solvent_volume, 4),
            "final_volume": round(final_volume, 4),
            "dilution_factor": round(mother_concentration / target_concentration, 4)
        }
