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
