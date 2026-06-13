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

    try:
        result = ConcentrationCalculator.calculate_solvent_volume(
            mother_concentration, target_concentration, mother_volume
        )
        return jsonify({
            "success": True,
            "input": {
                "mother_concentration": mother_concentration,
                "target_concentration": target_concentration,
                "mother_volume": mother_volume
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
