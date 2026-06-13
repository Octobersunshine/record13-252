import requests
import json

print('=== 浓度转换API功能测试 ===')
print()

print('1. 体积浓度 -> 质量浓度 (95%乙醇):')
resp = requests.post('http://127.0.0.1:5000/convert/v2m',
    json={'volume_percent': 95, 'solute_density': 0.789, 'solution_density': 0.804})
r = resp.json()['result']
print(f'   {r["volume_percent"]}% v/v -> {r["mass_percent"]:.2f}% w/w')
print(f'   质量体积浓度: {r["mass_volume_g_per_L"]:.2f} g/L')
print()

print('2. 质量浓度 -> 体积浓度 (75%乙醇):')
resp = requests.post('http://127.0.0.1:5000/convert/m2v',
    json={'mass_percent': 75, 'solute_density': 0.789, 'solution_density': 0.872})
r = resp.json()['result']
print(f'   {r["mass_percent"]}% w/w -> {r["volume_percent"]:.2f}% v/v')
print()

print('3. 通用转换 - NaCl摩尔浓度转g/L:')
resp = requests.post('http://127.0.0.1:5000/convert/general',
    json={'concentration_value': 0.154, 'from_unit': 'mol/L', 'to_unit': 'g/L',
          'molar_mass': 58.44})
r = resp.json()['result']
print(f'   生理盐水 {r["input"]["value"]} {r["input"]["unit"]}')
print(f'   = {r["output"]["value"]:.2f} {r["output"]["unit"]} (约0.9% w/v)')
print()

print('4. 通用转换 - 血糖mg/dL转mmol/L:')
resp = requests.post('http://127.0.0.1:5000/convert/general',
    json={'concentration_value': 100, 'from_unit': 'mg/dL', 'to_unit': 'mmol/L',
          'molar_mass': 180.16})
r = resp.json()['result']
print(f'   空腹血糖 {r["input"]["value"]} {r["input"]["unit"]}')
print(f'   = {r["output"]["value"]:.2f} {r["output"]["unit"]} (正常范围)')
print()

print('5. 通用转换 - 10% w/w 蔗糖溶液转w/v% (密度1.04 g/mL):')
resp = requests.post('http://127.0.0.1:5000/convert/general',
    json={'concentration_value': 10, 'from_unit': 'w/w%', 'to_unit': 'w/v%',
          'solution_density': 1.04})
r = resp.json()['result']
print(f'   {r["input"]["value"]} {r["input"]["unit"]} -> {r["output"]["value"]:.2f} {r["output"]["unit"]}')
print()

print('6. 通用转换 - 饮用水硬度ppm转mg/mL (CaCO3):')
resp = requests.post('http://127.0.0.1:5000/convert/general',
    json={'concentration_value': 300, 'from_unit': 'ppm', 'to_unit': 'mg/mL'})
r = resp.json()['result']
print(f'   硬水 {r["input"]["value"]} {r["input"]["unit"]}')
print(f'   = {r["output"]["value"]:.4f} {r["output"]["unit"]}')
print()

print('7. 错误测试 - 缺少密度参数:')
resp = requests.post('http://127.0.0.1:5000/convert/general',
    json={'concentration_value': 10, 'from_unit': 'w/w%', 'to_unit': 'g/L'})
print(f'   状态码: {resp.status_code}')
print(f'   错误: {resp.json()["error"]}')
print()

print('8. 错误测试 - 缺少摩尔质量参数:')
resp = requests.post('http://127.0.0.1:5000/convert/general',
    json={'concentration_value': 1, 'from_unit': 'g/L', 'to_unit': 'mol/L'})
print(f'   状态码: {resp.status_code}')
print(f'   错误: {resp.json()["error"]}')
print()

print('9. 错误测试 - 不支持的单位:')
resp = requests.post('http://127.0.0.1:5000/convert/general',
    json={'concentration_value': 10, 'from_unit': 'g/L', 'to_unit': 'unknown'})
print(f'   状态码: {resp.status_code}')
print(f'   错误: {resp.json()["error"][:50]}...')
print()

print('=== 所有API端点 ===')
print('POST /calculate        - 稀释配比计算')
print('POST /convert/v2m      - 体积% -> 质量%')
print('POST /convert/m2v      - 质量% -> 体积%')
print('POST /convert/general  - 通用单位转换 (26种单位)')
print('GET  /health           - 健康检查')
