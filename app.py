from flask import Flask, request, jsonify
from calculator import ConcentrationCalculator

app = Flask(__name__)


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    required_fields = ['mother_concentration', 'target_concentration', 'mother_volume']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"缺少必需参数: {field}"}), 400

    try:
        mother_concentration = float(data['mother_concentration'])
        target_concentration = float(data['target_concentration'])
        mother_volume = float(data['mother_volume'])
    except (ValueError, TypeError):
        return jsonify({"error": "所有参数必须为数值类型"}), 400

    correct_contraction = data.get('correct_contraction', False)
    if isinstance(correct_contraction, str):
        correct_contraction = correct_contraction.lower() in ['true', '1', 'yes']

    temperature = 20.0
    if 'temperature' in data:
        try:
            temperature = float(data['temperature'])
        except (ValueError, TypeError):
            return jsonify({"error": "temperature 必须为数值类型"}), 400

    manual_contraction_rate = None
    if 'manual_contraction_rate' in data and data['manual_contraction_rate'] is not None:
        try:
            manual_contraction_rate = float(data['manual_contraction_rate'])
        except (ValueError, TypeError):
            return jsonify({"error": "manual_contraction_rate 必须为数值类型"}), 400

    try:
        result = ConcentrationCalculator.calculate_solvent_volume(
            mother_concentration, target_concentration, mother_volume,
            correct_contraction=correct_contraction,
            temperature=temperature,
            manual_contraction_rate=manual_contraction_rate
        )
        return jsonify({
            "success": True,
            "input": {
                "mother_concentration": mother_concentration,
                "target_concentration": target_concentration,
                "mother_volume": mother_volume,
                "correct_contraction": correct_contraction,
                "temperature": temperature,
                "manual_contraction_rate": manual_contraction_rate
            },
            "result": result
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
