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
