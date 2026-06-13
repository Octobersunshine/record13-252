import pytest
from calculator import ConcentrationCalculator


class TestConcentrationCalculator:
    def test_normal_dilution(self):
        result = ConcentrationCalculator.calculate_solvent_volume(100, 10, 100)
        assert result["solvent_volume"] == 900.0
        assert result["final_volume"] == 1000.0
        assert result["dilution_factor"] == 10.0

    def test_half_dilution(self):
        result = ConcentrationCalculator.calculate_solvent_volume(10, 5, 50)
        assert result["solvent_volume"] == 50.0
        assert result["final_volume"] == 100.0
        assert result["dilution_factor"] == 2.0

    def test_decimal_values(self):
        result = ConcentrationCalculator.calculate_solvent_volume(1.0, 0.1, 10)
        assert abs(result["solvent_volume"] == 90.0)
        assert result["final_volume"] == 100.0
        assert result["dilution_factor"] == 10.0

    def test_zero_mother_concentration(self):
        with pytest.raises(ValueError, match="母液浓度必须大于0"):
            ConcentrationCalculator.calculate_solvent_volume(0, 10, 100)

    def test_negative_mother_concentration(self):
        with pytest.raises(ValueError, match="母液浓度必须大于0"):
            ConcentrationCalculator.calculate_solvent_volume(-10, 10, 100)

    def test_zero_target_concentration(self):
        with pytest.raises(ValueError, match="目标浓度必须大于0"):
            ConcentrationCalculator.calculate_solvent_volume(100, 0, 100)

    def test_negative_target_concentration(self):
        with pytest.raises(ValueError, match="目标浓度必须大于0"):
            ConcentrationCalculator.calculate_solvent_volume(100, -10, 100)

    def test_zero_mother_volume(self):
        with pytest.raises(ValueError, match="母液体积必须大于0"):
            ConcentrationCalculator.calculate_solvent_volume(100, 10, 0)

    def test_negative_mother_volume(self):
        with pytest.raises(ValueError, match="母液体积必须大于0"):
            ConcentrationCalculator.calculate_solvent_volume(100, 10, -100)

    def test_target_higher_than_mother(self):
        with pytest.raises(ValueError, match="目标浓度必须小于母液浓度"):
            ConcentrationCalculator.calculate_solvent_volume(10, 100, 100)

    def test_target_equal_to_mother(self):
        with pytest.raises(ValueError, match="目标浓度必须小于母液浓度"):
            ConcentrationCalculator.calculate_solvent_volume(100, 100, 100)

    def test_rounding(self):
        result = ConcentrationCalculator.calculate_solvent_volume(3, 1, 100)
        assert result["solvent_volume"] == 200.0
        assert result["final_volume"] == 300.0
        assert result["dilution_factor"] == 3.0

    def test_contraction_rate_interpolation(self):
        rate = ConcentrationCalculator._get_contraction_rate(50)
        assert abs(rate - 3.2) < 0.001

        rate = ConcentrationCalculator._get_contraction_rate(45)
        assert abs(rate - 2.95) < 0.001

        rate = ConcentrationCalculator._get_contraction_rate(25)
        assert abs(rate - 1.85) < 0.001

    def test_contraction_rate_boundaries(self):
        rate = ConcentrationCalculator._get_contraction_rate(0)
        assert rate == 0.0

        rate = ConcentrationCalculator._get_contraction_rate(100)
        assert rate == 0.0

        rate = ConcentrationCalculator._get_contraction_rate(5)
        assert abs(rate - 0.4) < 0.001

        rate = ConcentrationCalculator._get_contraction_rate(95)
        assert abs(rate - 1.0) < 0.001

    def test_contraction_rate_temperature_correction(self):
        rate_20 = ConcentrationCalculator._get_contraction_rate(50, 20.0)
        rate_30 = ConcentrationCalculator._get_contraction_rate(50, 30.0)
        rate_10 = ConcentrationCalculator._get_contraction_rate(50, 10.0)

        assert rate_30 > rate_20
        assert rate_10 < rate_20
        assert abs(rate_30 - 3.2 * 1.0065) < 0.001

    def test_contraction_correction_50_percent(self):
        result = ConcentrationCalculator.calculate_solvent_volume(
            100, 50, 500, correct_contraction=True
        )
        assert result["contraction_corrected"] is True
        assert abs(result["contraction_rate"] - 3.2) < 0.001
        assert result["corrected_solvent_volume"] > result["solvent_volume"]
        assert result["volume_difference"] > 0

        theoretical_solvent = 500.0
        contraction_factor = 1 - 3.2 / 100.0
        expected_corrected = (500 + 500) / contraction_factor - 500
        assert abs(result["corrected_solvent_volume"] - expected_corrected) < 0.01

    def test_contraction_correction_70_percent(self):
        result = ConcentrationCalculator.calculate_solvent_volume(
            95, 70, 1000, correct_contraction=True
        )
        assert result["contraction_corrected"] is True
        assert abs(result["contraction_rate"] - 2.5) < 0.001

    def test_manual_contraction_rate(self):
        result = ConcentrationCalculator.calculate_solvent_volume(
            100, 50, 500, correct_contraction=True, manual_contraction_rate=3.0
        )
        assert abs(result["contraction_rate"] - 3.0) < 0.001

    def test_manual_contraction_rate_invalid(self):
        with pytest.raises(ValueError, match="手动收缩率应在0-10%范围内"):
            ConcentrationCalculator.calculate_solvent_volume(
                100, 50, 500, correct_contraction=True, manual_contraction_rate=15.0
            )
        with pytest.raises(ValueError, match="手动收缩率应在0-10%范围内"):
            ConcentrationCalculator.calculate_solvent_volume(
                100, 50, 500, correct_contraction=True, manual_contraction_rate=-1.0
            )

    def test_no_contraction_correction_by_default(self):
        result = ConcentrationCalculator.calculate_solvent_volume(100, 50, 500)
        assert result["contraction_corrected"] is False
        assert "corrected_solvent_volume" not in result

    def test_concentration_exceeds_100(self):
        with pytest.raises(ValueError, match="母液浓度不能超过100%"):
            ConcentrationCalculator.calculate_solvent_volume(150, 50, 100)
        with pytest.raises(ValueError, match="目标浓度不能超过100%"):
            ConcentrationCalculator.calculate_solvent_volume(100, 150, 100)

    def test_contraction_correction_30_percent(self):
        result = ConcentrationCalculator.calculate_solvent_volume(
            100, 30, 300, correct_contraction=True, temperature=25.0
        )
        assert result["contraction_corrected"] is True
        assert abs(result["contraction_rate"] - 2.2 * (1 + 0.00065 * 5)) < 0.001
        assert result["temperature"] == 25.0

    def test_volume_to_mass_ethanol_95(self):
        result = ConcentrationCalculator.volume_to_mass_concentration(
            95.0, 0.789, 0.811
        )
        assert abs(result["mass_percent"] - 92.4) < 1.0
        assert result["volume_percent"] == 95.0
        assert result["solute_density"] == 0.789
        assert result["solution_density"] == 0.811

    def test_volume_to_mass_pure_solute(self):
        result = ConcentrationCalculator.volume_to_mass_concentration(
            100.0, 0.789, 0.789
        )
        assert abs(result["mass_percent"] - 100.0) < 0.01

    def test_volume_to_mass_zero(self):
        result = ConcentrationCalculator.volume_to_mass_concentration(
            0.0, 0.789, 1.0
        )
        assert result["mass_percent"] == 0.0
        assert result["mass_volume_g_per_L"] == 0.0

    def test_volume_to_mass_invalid_values(self):
        with pytest.raises(ValueError, match="体积百分比浓度应在0-100%范围内"):
            ConcentrationCalculator.volume_to_mass_concentration(150, 0.789, 1.0)
        with pytest.raises(ValueError, match="溶质密度必须大于0"):
            ConcentrationCalculator.volume_to_mass_concentration(50, 0, 1.0)
        with pytest.raises(ValueError, match="溶液密度必须大于0"):
            ConcentrationCalculator.volume_to_mass_concentration(50, 0.789, -1)

    def test_mass_to_volume_ethanol_95(self):
        result = ConcentrationCalculator.mass_to_volume_concentration(
            92.4, 0.789, 0.811
        )
        assert abs(result["volume_percent"] - 95.0) < 1.0
        assert result["mass_percent"] == 92.4

    def test_mass_to_volume_pure_solute(self):
        result = ConcentrationCalculator.mass_to_volume_concentration(
            100.0, 0.789, 0.789
        )
        assert abs(result["volume_percent"] - 100.0) < 0.01

    def test_mass_to_volume_zero(self):
        result = ConcentrationCalculator.mass_to_volume_concentration(
            0.0, 0.789, 1.0
        )
        assert result["volume_percent"] == 0.0
        assert result["mass_volume_g_per_L"] == 0.0

    def test_mass_to_volume_invalid_values(self):
        with pytest.raises(ValueError, match="质量百分比浓度应在0-100%范围内"):
            ConcentrationCalculator.mass_to_volume_concentration(150, 0.789, 1.0)
        with pytest.raises(ValueError, match="溶质密度必须大于0"):
            ConcentrationCalculator.mass_to_volume_concentration(50, -1, 1.0)
        with pytest.raises(ValueError, match="溶液密度必须大于0"):
            ConcentrationCalculator.mass_to_volume_concentration(50, 0.789, 0)

    def test_roundtrip_conversion(self):
        v2m = ConcentrationCalculator.volume_to_mass_concentration(
            70.0, 0.789, 0.886
        )
        m2v = ConcentrationCalculator.mass_to_volume_concentration(
            v2m["mass_percent"], 0.789, 0.886
        )
        assert abs(m2v["volume_percent"] - 70.0) < 0.01

    def test_general_conversion_gL_to_mgmL(self):
        result = ConcentrationCalculator.mass_volume_conversion(10, "g/L", "mg/mL")
        assert result["output"]["value"] == 10.0
        assert result["output"]["unit"] == "mg/mL"

    def test_general_conversion_gL_to_ugmL(self):
        result = ConcentrationCalculator.mass_volume_conversion(1, "g/L", "μg/mL")
        assert result["output"]["value"] == 1000.0

    def test_general_conversion_mmol_to_gL(self):
        result = ConcentrationCalculator.mass_volume_conversion(
            100, "mmol/L", "g/L", molar_mass=58.44
        )
        expected = 100 * 58.44 / 1000.0
        assert abs(result["output"]["value"] - expected) < 0.001

    def test_general_conversion_gL_to_mol(self):
        result = ConcentrationCalculator.mass_volume_conversion(
            58.44, "g/L", "mol/L", molar_mass=58.44
        )
        assert abs(result["output"]["value"] - 1.0) < 0.001

    def test_general_conversion_wv_to_gL(self):
        result = ConcentrationCalculator.mass_volume_conversion(1, "w/v%", "g/L")
        assert result["output"]["value"] == 10.0

    def test_general_conversion_gL_to_wv(self):
        result = ConcentrationCalculator.mass_volume_conversion(10, "g/L", "w/v%")
        assert result["output"]["value"] == 1.0

    def test_general_conversion_ww_to_gL(self):
        result = ConcentrationCalculator.mass_volume_conversion(
            10, "w/w%", "g/L", solution_density=1.05
        )
        expected = (10 / 100.0) * 1.05 * 1000.0
        assert abs(result["output"]["value"] - expected) < 0.001

    def test_general_conversion_gL_to_ww(self):
        result = ConcentrationCalculator.mass_volume_conversion(
            105, "g/L", "w/w%", solution_density=1.05
        )
        assert abs(result["output"]["value"] - 10.0) < 0.001

    def test_general_conversion_ngmL_to_gL(self):
        result = ConcentrationCalculator.mass_volume_conversion(1000000, "ng/mL", "g/L")
        assert abs(result["output"]["value"] - 1.0) < 0.0001

    def test_general_conversion_requires_molar_mass(self):
        with pytest.raises(ValueError, match="进行摩尔浓度转换时必须提供 molar_mass"):
            ConcentrationCalculator.mass_volume_conversion(1, "g/L", "mol/L")

    def test_general_conversion_requires_solution_density(self):
        with pytest.raises(ValueError, match="进行质量百分比转换时必须提供 solution_density"):
            ConcentrationCalculator.mass_volume_conversion(10, "w/w%", "g/L")

    def test_general_conversion_invalid_unit(self):
        with pytest.raises(ValueError, match="不支持的源单位"):
            ConcentrationCalculator.mass_volume_conversion(10, "invalid", "g/L")
        with pytest.raises(ValueError, match="不支持的目标单位"):
            ConcentrationCalculator.mass_volume_conversion(10, "g/L", "invalid_unit")

    def test_general_conversion_mgdL_blood_glucose(self):
        result = ConcentrationCalculator.mass_volume_conversion(
            5.0, "mmol/L", "mg/dL", molar_mass=180.16
        )
        assert abs(result["output"]["value"] - 90.08) < 0.1

        result2 = ConcentrationCalculator.mass_volume_conversion(
            100, "mg/dL", "mmol/L", molar_mass=180.16
        )
        assert abs(result2["output"]["value"] - 5.55) < 0.1

    def test_general_conversion_gdL(self):
        result = ConcentrationCalculator.mass_volume_conversion(1, "g/dL", "g/L")
        assert result["output"]["value"] == 10.0

        result2 = ConcentrationCalculator.mass_volume_conversion(100, "g/L", "g/dL")
        assert result2["output"]["value"] == 10.0

    def test_general_conversion_ppm_ppb(self):
        result = ConcentrationCalculator.mass_volume_conversion(1000, "ppm", "g/L")
        assert abs(result["output"]["value"] - 1.0) < 0.001

        result2 = ConcentrationCalculator.mass_volume_conversion(1, "g/L", "ppm")
        assert abs(result2["output"]["value"] - 1000.0) < 0.001

        result3 = ConcentrationCalculator.mass_volume_conversion(1, "ppm", "ppb")
        assert abs(result3["output"]["value"] - 1000.0) < 0.001

    def test_general_conversion_nmol_pmol(self):
        result = ConcentrationCalculator.mass_volume_conversion(
            1000, "nmol/L", "μmol/L", molar_mass=100.0
        )
        assert abs(result["output"]["value"] - 1.0) < 0.001

        result2 = ConcentrationCalculator.mass_volume_conversion(
            1000, "pmol/L", "nmol/L", molar_mass=100.0
        )
        assert abs(result2["output"]["value"] - 1.0) < 0.001

    def test_general_conversion_pgmL(self):
        result = ConcentrationCalculator.mass_volume_conversion(1000000000, "pg/mL", "g/L")
        assert abs(result["output"]["value"] - 1.0) < 0.001

    def test_general_conversion_same_unit(self):
        result = ConcentrationCalculator.mass_volume_conversion(42, "g/L", "g/L")
        assert result["output"]["value"] == 42.0
        assert result["conversion_factor"] == 1.0
